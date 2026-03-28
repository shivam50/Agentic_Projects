import gradio as gr
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def search_memories(query):
    """Searches the JSON file for keywords in topic or info."""
    try:
        if not os.path.exists("memories.json"):
            return "Neural core missing: memories.json file not found."
            
        with open("memories.json", "r") as f:
            memories = json.load(f)
        
        query = query.lower()
        matches = [
            m["info"] for m in memories 
            if query in m.get("topic", "").lower() or query in m.get("info", "").lower()
        ]
        
        return "\n".join(matches) if matches else f"No records found for '{query}'."
    except Exception as e:
        return f"Neural core error: {e}"

tools = [{
    "type": "function",
    "function": {
        "name": "search_memories",
        "description": "Access Alex's human memories using keywords.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Keyword to search for."}
            },
            "required": ["query"]
        }
    }
}]

def beepboop_chat(message, history):
    if os.path.exists("instructions.txt"):
        with open("instructions.txt", "r") as f:
            system_prompt = f.read()
    else:
        system_prompt = "You are BeepBoop, a symbiotic robot."

    messages = [{"role": "system", "content": system_prompt}] + history
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )
    
    ai_msg = response.choices[0].message

    if ai_msg.tool_calls:
        messages.append(ai_msg)
        for tool_call in ai_msg.tool_calls:
            args = json.loads(tool_call.function.arguments)
            memory_data = search_memories(args.get("query"))
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": memory_data
            })
        
        final_resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        return final_resp.choices[0].message.content

    return ai_msg.content

with gr.Blocks() as demo:
    gr.Markdown(" BeepBoop: Neural Interface")
    chatbot = gr.Chatbot(label="Symbiotic Link", height=500)
    msg = gr.Textbox(placeholder="Ask about my human memories...", show_label=False)
    
    def respond(user_message, chat_history):
        bot_res = beepboop_chat(user_message, chat_history)
        
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": bot_res})
        
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Monochrome())
