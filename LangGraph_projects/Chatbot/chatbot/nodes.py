from langchain_openai import ChatOpenAI
from chatbot.state import MessageState
from dotenv import load_dotenv


load_dotenv()


llm = ChatOpenAI(model="gpt-4o-mini")

def call_model(state: MessageState):
    '''  Calls the LLM with the current messages '''
    response = llm.invoke(state["messages"])
    return {"messages": [response]}