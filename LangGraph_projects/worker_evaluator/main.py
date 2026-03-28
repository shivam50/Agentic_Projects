import uuid
import asyncio
from typing import Annotated, TypedDict, List, Dict, Any, Optional

import gradio as gr
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Core Playwright and LangGraph imports
from playwright.async_api import async_playwright
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

# 1. SETUP
load_dotenv(override=True)

class EvaluatorOutput(BaseModel):
    feedback: str = Field(description="Feedback on the assistant's response")
    success_criteria_met: bool = Field(description="Whether the success criteria have been met")

class State(TypedDict):
    messages: Annotated[List[Any], add_messages]
    success_criteria: str
    feedback_on_work: Optional[str]
    success_criteria_met: bool

# ==========================================
# 2. THE LAZY LOADER
# ==========================================
# We store these globally so they persist across different user clicks
COMPILED_GRAPH = None
PLAYWRIGHT_INSTANCE = None
BROWSER_INSTANCE = None

async def get_lazy_graph():
    """ Initializes Playwright and Graph ONLY when first called. """
    global COMPILED_GRAPH, PLAYWRIGHT_INSTANCE, BROWSER_INSTANCE

    if COMPILED_GRAPH is not None:
        return COMPILED_GRAPH

    print("--- 🚀 Lazy Initializing Playwright and AI Graph ---")
    
    # Start Playwright inside the current Gradio loop
    PLAYWRIGHT_INSTANCE = await async_playwright().start()
    BROWSER_INSTANCE = await PLAYWRIGHT_INSTANCE.chromium.launch(headless=False)
    
    # Setup Toolkit
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=BROWSER_INSTANCE)
    tools = toolkit.get_tools()

    # Setup LLMs
    worker_llm = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)
    evaluator_llm = ChatOpenAI(model="gpt-4o-mini").with_structured_output(EvaluatorOutput)

    # --- Node Definitions ---
    def worker(state: State):
        sys_msg = SystemMessage(content=f"Complete the task. Criteria: {state['success_criteria']}")
        # Combine system message with conversation history
        msgs = [sys_msg] + state["messages"]
        return {"messages": [worker_llm.invoke(msgs)]}

    def worker_router(state: State):
        if state["messages"][-1].tool_calls:
            return "tools"
        return "evaluator"

    def evaluator(state: State):
        last_msg = state["messages"][-1].content
        res = evaluator_llm.invoke([
            SystemMessage(content="Evaluate the response."),
            HumanMessage(content=f"Criteria: {state['success_criteria']}\nAnswer: {last_msg}")
        ])
        return {
            "messages": [AIMessage(content=f"Evaluator: {res.feedback}")],
            "success_criteria_met": res.success_criteria_met
        }

    # --- Build Graph ---
    workflow = StateGraph(State)
    workflow.add_node("worker", worker)
    workflow.add_node("tools", ToolNode(tools=tools))
    workflow.add_node("evaluator", evaluator)

    workflow.add_conditional_edges("worker", worker_router, {"tools": "tools", "evaluator": "evaluator"})
    workflow.add_edge("tools", "worker")
    workflow.add_conditional_edges("evaluator", lambda s: "END" if s["success_criteria_met"] else "worker", {"END": END, "worker": "worker"})
    workflow.add_edge(START, "worker")

    COMPILED_GRAPH = workflow.compile(checkpointer=MemorySaver())
    print("--- ✅ System Ready ---")
    return COMPILED_GRAPH
# ==========================================
# 3. GRADIO INTERFACE (Fixed for Gradio 6.0)
# ==========================================
async def handle_submit(message, criteria, history, thread_id):
    graph = await get_lazy_graph()
    
    config = {"configurable": {"thread_id": thread_id}}
    
    # We pass the message history into the graph state
    input_state = {
        "messages": [HumanMessage(content=message)],
        "success_criteria": criteria,
        "success_criteria_met": False
    }

    result = await graph.ainvoke(input_state, config=config)
    
    # In Gradio 6, we append dictionaries directly to the history list
    history.append({"role": "user", "content": message})
    
    # result["messages"][-2] is usually the Worker's response 
    # (since the Evaluator adds the very last message)
    history.append({"role": "assistant", "content": result["messages"][-2].content})
    
    return history

def main():
    with gr.Blocks() as demo:
        gr.Markdown("# Lazy Sidekick (Playwright + LangGraph)")
        
        # Initialize thread state
        thread = gr.State(lambda: str(uuid.uuid4()))
        
        # REMOVED: type="messages" (Not needed in Gradio 6)
        chatbot = gr.Chatbot(label="Chat", height=400)
        
        with gr.Row():
            msg = gr.Textbox(label="Your Request", placeholder="e.g. Find the price of Nvidia stock")
            crit = gr.Textbox(label="Success Criteria", placeholder="e.g. The exact price is found")
        
        btn = gr.Button("Go", variant="primary")

        # Link components
        btn.click(handle_submit, [msg, crit, chatbot, thread], [chatbot])

    # Launch the server
    demo.launch()

if __name__ == "__main__":
    main()