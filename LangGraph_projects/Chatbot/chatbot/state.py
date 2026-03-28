from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
import operator


class MessageState(TypedDict):
    messages: Annotated[list, add_messages]


    