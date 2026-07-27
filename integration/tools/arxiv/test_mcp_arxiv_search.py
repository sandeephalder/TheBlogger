import asyncio
import os
import sys
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

def test_mcp_search_arxiv_server():
    """Integration test connecting to arXiv MCP server via stdio transport."""
    async def _run():
        server_script = os.path.abspath("tools/arxiv_tool.py")
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script],
            env=os.environ.copy(),
        )

        print("🚀 Connecting to Python arXiv MCP Server...")
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("✅ Connection initialized successfully.")

                tools_response = await session.list_tools()
                tool_names = [t.name for t in tools_response.tools]
                assert "search_arxiv_papers" in tool_names

                print("\n🔍 Invoking 'search_arxiv_papers' tool...")
                result = await session.call_tool("search_arxiv_papers", arguments={"query": "Attention", "max_results": 1})
                assert result.content is not None
                assert len(result.content) > 0
                assert any(c.type == "text" for c in result.content)

                print("\n📥 Server Response Content:")
                print("-" * 40)
                for content in result.content:
                    if content.type == "text":
                        print(content.text)
                print("-" * 40)

    asyncio.run(_run())


if __name__ == "__main__":
    test_mcp_search_arxiv_server()
