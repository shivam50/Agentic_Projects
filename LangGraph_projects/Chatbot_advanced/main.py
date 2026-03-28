import gradio as gr
from langgraph.graph import StateGraph, START, END
from state import State
from nodes import chatbot_node

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


def main(user_input: str, history):
    initial_state = {"messages": [{"role": "user", "content":user_input}]}
    result = graph.invoke(initial_state)

    return result["messages"][-1].content


if __name__ == "__main__":
    print("------Launching Chatbot UI ------")
    gr.ChatInterface(fn=main).launch()
