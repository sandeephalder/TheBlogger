import asyncio
import os
import sys
import pytest
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

load_dotenv()

def test_mcp_wordpress_get_server():
    """Integration test invoking list_recent_posts over MCP stdio transport."""
    async def _run():
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["tools/wordpress_tool.py"],
            env=os.environ.copy()
        )
        
        print("🚀 Connecting to Python WordPress MCP Server...")
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("✅ Connection initialized successfully.")

                tools_response = await session.list_tools()
                tool_names = [tool.name for tool in tools_response.tools]
                assert "list_recent_posts" in tool_names

                print("\n📦 Invoking 'list_recent_posts' tool...")
                result = await session.call_tool("list_recent_posts", arguments={"per_page": 2})
                assert result.content is not None
                assert len(result.content) > 0

                print("\n📥 Server Response Content:")
                print("-" * 40)
                for content in result.content:
                    if content.type == "text":
                        print(content.text)
                print("-" * 40)

    asyncio.run(_run())


if __name__ == "__main__":
    test_mcp_wordpress_get_server()
