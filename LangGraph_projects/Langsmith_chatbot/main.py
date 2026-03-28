from typing import Annotated
from unittest import result
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import gradio as gr
from langgraph.prebuilt import ToolNode, tools_condition
import requests
import os
from langchain_openai import ChatOpenAI
from typing import TypedDict
from langchain_core.tools import Tool
from IPython.display import Image, display
from langchain_community.utilities import GoogleSerperAPIWrapper
from langgraph.checkpoint.memory import MemorySaver
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver




load_dotenv(override=True)

db_path = "memory.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
sql_memory = SqliteSaver(conn)

pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user = os.getenv("PUSHOVER_USER")
pushover_url = os.getenv("PUSHOVER_URL")


serper = GoogleSerperAPIWrapper()



#Defining Tools

tool_search = Tool(
    name="search",
    func=serper.run,
    description="Useful for when you need more information from an online spend"
)


def push(text: str):
    """Send a push notification to the user"""
    requests.post(pushover_url, data = {"token": pushover_token, "user": pushover_user, "message": text})

tool_push = Tool(
    name="send_push_notification",
    func=push,
    description="useful when to send push notif"
)

tool_push.invoke("Hello, me")

tools = [tool_search, tool_push]

#Defining State Object

class State(TypedDict):
    messages: Annotated[list, add_messages]

#Start the Graph Builder with this State class
graph_builder = StateGraph(State)

llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)


#Create a Node

def chatbot(state: State):
    return{"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

#Create Edges

graph_builder.add_conditional_edges("chatbot", tools_condition, "tools")

#Any time a tool is called we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

#Compile graph

graph = graph_builder.compile(checkpointer=sql_memory)

config = {"configurable":{"thread_id": "3"}}


def chat(user_input: str, history):
    result = graph.invoke({"messages": [{"role": "user", "content": user_input}]}, config=config)
    return result["messages"][-1].content

demo = gr.ChatInterface(chat)

if __name__ == "__main__":
    demo.launch()