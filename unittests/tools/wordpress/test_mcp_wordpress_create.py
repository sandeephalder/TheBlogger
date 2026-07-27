import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

async def run_test():
    server_params = StdioServerParameters(
        command="python",
        args=["tools/wordpress_tool.py"],
        env=os.environ.copy()
    )
    
    print("🚀 Connecting to Python WordPress MCP Server...")
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("✅ Connection initialized.")
            
            # Target our new creation tool
            print("\n✍️ Sending post creation request to server...")
            
            post_arguments = {
                "title": "My First Automated MCP Post",
                "content": "<p>This article was published seamlessly using a custom Python MCP server tool structure!</p>",
                "status": "draft"  # Set to "publish" if you want it immediately live
            }
            
            result = await session.call_tool("create_new_post", arguments=post_arguments)
            
            print("\n📥 Server Response Content:")
            print("-" * 40)
            for content in result.content:
                if content.type == "text":
                    print(content.text)
            print("-" * 40)

if __name__ == "__main__":
    asyncio.run(run_test())
