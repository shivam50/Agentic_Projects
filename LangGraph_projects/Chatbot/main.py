import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from chatbot.state import MessageState
from chatbot.nodes import call_model
from langgraph.checkpoint
# Load your .env file
load_dotenv()

# 1. Create the Graph builder
workflow = StateGraph(MessageState)

# 2. Add the node we defined
workflow.add_node("agent", call_model)

# 3. Set the flow
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

# 4. Compile the graph into an executable app
app = workflow.compile()

if __name__ == "__main__":
    # Test the graph
    inputs = {"messages": [("user", "Hello! Who are you?")]}
    
    print("--- Running Graph ---")
    for event in app.stream(inputs):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)