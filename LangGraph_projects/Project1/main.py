import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from chatbot.state import MessageState
from chatbot.nodes import call_model
from langgraph.checkpoint
load_dotenv()

workflow = StateGraph(MessageState)

workflow.add_node("agent", call_model)

workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

app = workflow.compile()

if __name__ == "__main__":
    inputs = {"messages": [("user", "Hello! Who are you?")]}
    
    print("--- Running Graph ---")
    for event in app.stream(inputs):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)