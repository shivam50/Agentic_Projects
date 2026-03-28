from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import Tool
import os
import requests
from langchain.tools import tool
import datetime
from dotenv import load_dotenv # Add this


load_dotenv()


serper = GoogleSerperAPIWrapper()
#serper tool for search
tool_search = Tool(
    name="search",
    func=serper.run,
    description="Useful for when you need more information from an online search"
)



pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user = os.getenv("PUSHOVER_USER")
pushover_url = "https://api.pushover.net/1/messages.json"

#push notif tool


def push(text: str):
    requests.post(pushover_url, data = {"token": pushover_token, "user": pushover_user, "message": text})


tool_push = Tool(
    name="push",
    func=push,
    description="Useful when you want to send a push notification"
)

#date-time context tool

def current_time():
    "returns current date and time"
    return str(datetime.datetime.now())

#wikipedia tool
def wiki(text: str):
    wikipedia.run(text)

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())


tool_wiki = Tool(
    name="wiki",
    func=wiki,
    description="Useful for structured output on a topic"
)


#combining tools
tools = [tool_search, tool_push, tool_wiki]