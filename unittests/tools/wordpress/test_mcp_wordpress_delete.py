import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

async def run_test():
    # Configure the client to spawn and talk to your Python server
    server_params = StdioServerParameters(
        command="python",
        args=["tools/wordpress_tool.py"],
        env=os.environ.copy()
    )
    
    print("🚀 Connecting to Python WordPress MCP Server...")
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Step 1: Initialize connection
            await session.initialize()
            print("✅ Connection initialized successfully.")
            
            # Step 2: List available tools to ensure discovery works
            print("\n🔍 Fetching available tools...")
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                print(f"   Found tool: {tool.name} - {tool.description}")
            
            # Step 3: Directly call your WordPress tool
            print("\n🗑️ Sending post deletion request...")
            delete_arguments = {
                "post_id": 55,  # 👈 Replace with your actual post ID number
                "force": False    # Set to True if you want to bypass Trash completely
            }
            result = await session.call_tool("delete_post", arguments=delete_arguments) 
            
            print("\n📥 Server Response Content:")
            print("-" * 40)
            # Display text contents returned from your server
            for content in result.content:
                if content.type == "text":
                    print(content.text)
            print("-" * 40)

if __name__ == "__main__":
    asyncio.run(run_test())
