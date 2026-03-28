import os
import requests
import gradio as gr
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

# LangChain / LangGraph imports
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# Playwright ASYNC imports
from playwright.async_api import async_playwright
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit

load_dotenv(override=True)

#State & Basic Tool Setup

class State(TypedDict):
    messages: Annotated[list, add_messages]

pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user = os.getenv("PUSHOVER_USER")
pushover_url = "https://api.pushover.net/1/messages.json"

def push(text: str):
    """Send a push notification to the user"""
    requests.post(pushover_url, data={"token": pushover_token, "user": pushover_user, "message": text})

tool_push = Tool(
    name="send_push_notification",
    func=push,
    description="useful for when you want to send a push notification"
)

# Gradio Chat Interface with Context Manager
memory = MemorySaver()
config = {"configurable": {"thread_id": "10"}}

async def chat(user_input: str, history):
    print("\n⏳ Starting fresh Playwright context for this query...")
    
    # Use 'async with' to guarantee the browser stays alive for the whole turn
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        
        # Explicitly create a context and a page for our relaxed tool to use
        context = await browser.new_context()
        page = await context.new_page()
        
        # Load default LangChain tools
        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
        base_tools = toolkit.get_tools()
        
        # --- CUSTOM RELAXED NAVIGATE TOOL ---
        # We build this to override Langchain's strict timeout settings
        async def relaxed_navigate(url: str) -> str:
            try:
                # wait_until="domcontentloaded" prevents CNN and heavy sites from timing out
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                return f"Successfully navigated to {url}"
            except Exception as e:
                return f"Failed to navigate to {url}: {e}"

        relaxed_nav_tool = Tool(
            name="navigate_browser",
            description="Navigate a browser to the specified URL",
            func=lambda x: "Use async run",
            coroutine=relaxed_navigate
        )
        
        # Swap out the strict navigate tool for our relaxed one
        filtered_base_tools = [t for t in base_tools if t.name != "navigate_browser"]
        all_tools = [relaxed_nav_tool] + filtered_base_tools + [tool_push]
        
        # Bind LLM
        llm = ChatOpenAI(model="gpt-4o-mini")
        llm_with_tools = llm.bind_tools(all_tools)

        def chatbot(state: State):
            return {"messages": [llm_with_tools.invoke(state["messages"])]}

        # Build Graph
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_node("tools", ToolNode(tools=all_tools))
        graph_builder.add_conditional_edges("chatbot", tools_condition, "tools")
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.add_edge(START, "chatbot")

        graph = graph_builder.compile(checkpointer=memory)
        
        # Run the agent
        print(" Agent is thinking and browsing...")
        result = await graph.ainvoke(
            {"messages": [{"role": "user", "content": user_input}]}, 
            config=config
        )
        
        # The 'async with' block will now cleanly close the browser when done
        print(" Finished query. Closing browser.")
        return result["messages"][-1].content


if __name__ == "__main__":
    print("Launching Gradio Server...")
    gr.ChatInterface(chat).launch()