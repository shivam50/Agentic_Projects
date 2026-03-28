from agents import Agent
from sdr_agent import write_mail, pii_output_guardrail
import asyncio
import json
from typing import override
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
from dotenv import load_dotenv
import os


manager_instruction = """
You are the Sales Manager at ComplAI. 
Your job is to:
1. Take the user's lead information.
2. Call 'write_mail' and pass that lead information into the 'user_request' parameter.
3. Review the 3 resulting drafts.
4. Pick the winner and transfer to the ClosingSpecialist.
"""
load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



closer_agent = Agent(name="ClosingSpecialist", instructions="You take approved drafts and finalize the sending logic. You Display the best mail selected")

async def run_sales_team(lead_info):
    manager = Agent(
        name="SalesManager",
        instructions=manager_instruction,
        model='gpt-4o-mini',
        tools=[write_mail],
        handoffs=[closer_agent]
    )


    with trace("Automated SDR"):
        result = await Runner.run(manager, lead_info)
    return result.final_output



