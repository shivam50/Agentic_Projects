from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict



#define state obj
class State(TypedDict):
    messages: Annotated[list, add_messages]

