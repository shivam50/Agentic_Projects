from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
import os


load_dotenv(override=True)






instructions = """
You browse the internet to accomplish your instructions.
You are highly capable at browsing the internet independently to accomplish your task, 
including accepting all cookies and clicking 'not now' as
appropriate to get to the content you need. If one website isn't fruitful, try another. 
Be persistent until you have solved your assignment,
trying different options and sites as needed.
When you need to write files, you do that inside the sandbox folder only.
"""

async def agent_run(instructions):
    fetch_params = {"command": "uvx", "args": ["mcp-server-fetch"]}

    #start mcp server process, opens a connection to it and asks what tools you have? stores them in fetch_tools
    async with MCPServerStdio(params=fetch_params, client_session_timeout_seconds=30) as server:
        fetch_tools = await server.list_tools()
    playwright_params = {"command": "npx","args": [ "@playwright/mcp@latest"]}
    async with MCPServerStdio(params=playwright_params, client_session_timeout_seconds=30) as server:
        playwright_tools = await server.list_tools()
    sandbox_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox"))
    if not os.path.exists(sandbox_path):
        print(f"Creating directory: {sandbox_path}")
        os.makedirs(sandbox_path)
    sandbox_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox"))
    files_params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox_path]}

    async with MCPServerStdio(params=files_params,client_session_timeout_seconds=60) as server:
        file_tools = await server.list_tools()

    async with MCPServerStdio(params=files_params, client_session_timeout_seconds=60) as mcp_server_files:
        async with MCPServerStdio(params=playwright_params, client_session_timeout_seconds=60) as mcp_server_browser:
            agent = Agent(
                name="investigator", 
                instructions=instructions, 
                model="gpt-4.1-mini",
                mcp_servers=[mcp_server_files, mcp_server_browser]
                )
            with trace("investigate"):
                result = await Runner.run(agent, "Find a great recipe for Banoffee Pie, then summarize it in markdown to banoffee.md")
                print(result.final_output)

import asyncio
asyncio.run(agent_run(instructions))