import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Define how to launch the server
    server_params = StdioServerParameters(
        command="python3",
        args=["my_server.py"],
    )

    # Connect via stdio transport
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            # 1. Initialize session (handshake)
            await session.initialize()
            print("✓ Connected to server")

            # 2. List available tools
            tools_result = await session.list_tools()
            print(f"\n📦 Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description[:60]}...")

            # 3. Call the calculate tool
            print("\n🔧 Calling 'calculate'...")
            result = await session.call_tool("calculate", {"expression": "42 * 1337"})
            print(f"  Result: {result.content[0].text}")

            # 4. Call the convert_units tool
            print("\n🔧 Calling 'convert_units'...")
            result = await session.call_tool(
                "convert_units",
                {"value": 100.0, "from_unit": "km", "to_unit": "miles"}
            )
            print(f"  Result: {result.content[0].text}")

            # 5. Read a resource
            print("\n📄 Reading resource 'info://supported-conversions'...")
            resource_result = await session.read_resource("info://supported-conversions")
            print(f"  Content:\n{resource_result.contents[0].text}")


asyncio.run(main())