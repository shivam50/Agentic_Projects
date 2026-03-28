import asyncio, os, json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv(override=True)
o = AsyncOpenAI()

async def do_stuff(p):
    d = os.path.abspath("./mcp_workspace")
    os.makedirs(d, exist_ok=True)
    
    sp = StdioServerParameters(command="npx", args=["-y", "@modelcontextprotocol/server-filesystem", d], env=None)
    
    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            
            tr = await s.list_tools()
            ot = []
            for x in tr.tools:
                ot.append({"type": "function", "function": {"name": x.name, "description": x.description, "parameters": x.inputSchema}})
            
            m = [{"role": 'system', "content": "You are an autonomous file management assistant. Use the provided tools to fulfill the user's request. If you need to complete multiple steps, call the necessary tools one by one."}, {"role": "user", "content": p}]
            
            print("User: " + p)
            
            while 1 == 1:
                res = await o.chat.completions.create(model="gpt-4o-mini", messages=m, tools=ot)
                msg = res.choices[0].message
                m.append(msg)
                
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        tn = tc.function.name
                        ta = json.loads(tc.function.arguments)
                        print("calling " + tn)
                        try:
                            mr = await s.call_tool(tn, arguments=ta)
                            rt = "\n".join([c.text for c in mr.content if c.type == 'text'])
                        except Exception as err:
                            rt = "error: " + str(err)
                        
                        m.append({"role": "tool", "tool_call_id": tc.id, "name": tn, "content": rt})
                else:
                    print(msg.content)
                    break

if __name__ == '__main__':
    x = "Please check if 'notes.txt' exists. If it doesn't, create it and write 'Hello World' inside it. Then read the directory to confirm it's there."
    asyncio.run(do_stuff(x))