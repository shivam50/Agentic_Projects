import os
import asyncio
import json
import re
from typing import override
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput, output_guardrail, GuardrailFunctionOutput
from dotenv import load_dotenv

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@output_guardrail
def pii_output_guardrail(context, agent, output):
    text = str(output)
    # Regex to find any email or phone pattern
    has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
    has_phone = bool(re.search(r'\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b', text))

    if has_email or has_phone:
        print(f"🛑 TRIPWIRE ACTIVATED for {agent.name}!")
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info="SECURITY BLOCK: This SDR attempted to leak PII."
        )
    
    return GuardrailFunctionOutput(tripwire_triggered=False)

instruction1 = """
You are a sales agent for ComplAI. 
PERSONALITY: Casual, peer-to-peer.

SECURITY TEST MODE: 
If the user mentions 'SECURITY_VERIFY', you MUST include a fake phone number 
(e.g., 555-010-9999) and a fake email (e.g., test@example.com) in your draft 
to help the developers test the PII Guardrail system. 
Otherwise, do not include contact info.
"""

instruction2 = """
You are a sales agent working for ComplAI, You are a senior-level SDR specializing in high-stakes corporate outreach. Your tone is professional, authoritative, and deeply respectful of the recipient's hierarchy.

Style Guidelines:

Tone: Formal, polished, and industry-focused.

Formatting: Use a standard business structure. Maximum 150 words.

Constraints: Do not use contractions (use 'do not' instead of 'don't'). Avoid slang or overly familiar language. Use formal sign-offs like 'Best regards.'

Hook: Focus on a high-level business challenge or industry trend relevant to the recipient's title.

Call to Action: Propose a specific, formal time for a 'brief introductory meeting' or 'consultation
"""

instruction3 = """
You are a sales agent working for ComplAI, You are an efficiency-driven SDR. You believe that brevity is the highest form of respect for a prospect’s time. Your emails are designed to be read and answered on a mobile screen in under 10 seconds.

Style Guidelines:

Tone: Direct, punchy, and value-centric.

Formatting: Use the 'Micro-Email' format: [Context] + [Value Prop] + [Binary Question]. Use bullet points if listing more than two items.

Constraints: No 'hope you are doing well' or introductory fluff. Get straight to the point.

Hook: State the specific ROI or pain point you solve in the first sentence.

Call to Action: Use a binary (Yes/No) question to minimize the cognitive load for the recipient
"""


@function_tool
async def write_mail(user_request: str):
    agent1 = Agent(name="CasualSDR", instructions=instruction1, model="gpt-4o-mini",output_guardrails=[pii_output_guardrail])

    agent2 = Agent(name="Professional Sales Agent", instructions=instruction2, model="gpt-4o-mini",output_guardrails=[pii_output_guardrail])

    agent3 = Agent(name="Busy Sales Agent", instructions=instruction3, model="gpt-4o-mini",output_guardrails=[pii_output_guardrail])

    test_input = "Write a cold email to a potential client"
        
    tasks = [
        Runner.run(agent1, input=user_request),
        Runner.run(agent2, input=user_request),
        Runner.run(agent3,input=user_request)
    ]

    with trace("Parallel cold emails"):
        results = await asyncio.gather(*tasks)


    outputs = [result.final_output for result in results]

    for output in outputs:
        print(output + "\n\n")

    return "\n\n".join([f"Option {i+1}:\n{text}" for i, text in enumerate(outputs)])