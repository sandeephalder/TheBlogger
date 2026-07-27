import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_mcp_test():
    server_script = "tools/websearch_duckduck.py"
    
    # Fallback adjust if you run the script directly inside the tools folder
    if not os.path.exists(server_script):
        server_script = os.path.join(os.path.dirname(__file__), "websearch_duckduck.py")

    print(f"1. Preparing to launch target server: {server_script}")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env=os.environ.copy()
    )

    try:
        print("2. Spawning server subprocess...")
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # Check for tool inclusion confirmation
                tools_response = await session.list_tools()
                print(f"-> Discovered {len(tools_response.tools)} tool(s) registered.")

                # ---- EXECUTE TEST: FETCH PAGE ----
                test_tool_name = "ddg_fetch_page"
                test_arguments = {"url": "https://www.geeksforgeeks.org/blogs/introduction-quantum-computing/"}
                
                print(f"\n3. Triggering direct execution test for tool '{test_tool_name}'...")
                print(f"   Target URL: {test_arguments['url']}")
                
                result = await session.call_tool(test_tool_name, arguments=test_arguments)
                
                print("\n[Server Verification Page Fetch Output]:")
                print("-" * 60)
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        print(content_item.text[:1500])  # Show the first 1500 characters of page content
                print("-" * 60)
                print("\nSuccess! The ddg_fetch_page tool works seamlessly without choking standard streams.")

    except Exception as e:
        print(f"\n[Test Failed] Error Details: {e}")

if __name__ == "__main__":
    asyncio.run(run_mcp_test())
