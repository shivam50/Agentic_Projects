import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from state import State


load_dotenv()

llm = ChatOpenAI(model='gpt-4o-mini')

def chatbot_node(old_state: State) -> dict:
    response = llm.invoke(old_state.messages)
    return {"messages": [response]}

