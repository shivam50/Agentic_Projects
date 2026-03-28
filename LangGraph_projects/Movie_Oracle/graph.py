from langgraph.graph import StateGraph, START, END
from state import State
from tools import tools
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)


#Node
def call_model(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


#Define graph:

graph_builder = StateGraph(State)
graph_builder.add_node("agent", call_model)
graph_builder.add_node("tools", ToolNode(tools=tools))


#Edges:

graph_builder.add_conditional_edges("agent", tools_condition, "tools")

graph_builder.add_edge("tools", "agent")
graph_builder.add_edge(START, "agent")


#Compile graph
movie_app = graph_builder.compile()


