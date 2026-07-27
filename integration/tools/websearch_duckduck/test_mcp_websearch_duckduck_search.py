import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_mcp_test():
    # 1. Define the path to your server script
    # This automatically finds 'custom_ddg_mcp_server.py' in the current working directory
    server_script = "tools/websearch_duckduck.py"
    
    if not os.path.exists(server_script):
        print(f"Error: Could not find server file at {server_script}")
        print("Please place this test script in the same directory as your server script.")
        return

    print(f"1. Preparing to launch target server: {server_script}")

    # 2. Configure the Stdio parameters to launch your Python script as a server
    server_params = StdioServerParameters(
        command=sys.executable,  # Uses the current active Python interpreter executable
        args=[server_script],
        env=os.environ.copy()    # Passes your current terminal environment variables along
    )

    try:
        print("2. Spawning server subprocess and establishing Stdio connection pipes...")
        # 3. Connect to the server process via stdin/stdout streams
        async with stdio_client(server_params) as (read_stream, write_stream):
            
            # 4. Open a communication session with the MCP server
            async with ClientSession(read_stream, write_stream) as session:
                print("-> Stdio session successfully handshake initialized.")
                
                # 5. Initialize the session protocol exchange
                await session.initialize()
                print("3. Fetching list of registered tools from your server...")
                
                # 6. Request the available tools
                tools_response = await session.list_tools()
                available_tools = tools_response.tools
                
                print(f"-> Discovered {len(available_tools)} tool(s) registered on your server:")
                for tool in available_tools:
                    print(f"   - [{tool.name}]: {tool.description[:60]}...")

                # 7. Target the 'ddg_web_search' tool for a functional query test
                test_tool_name = "ddg_web_search"
                test_arguments = {"query": "Quantum Computing"}
                
                print(f"\n4. Triggering direct execution test for tool '{test_tool_name}'...")
                print(f"   Arguments: {test_arguments}")
                
                # 8. Call the tool inside the server
                result = await session.call_tool(test_tool_name, arguments=test_arguments)
                
                # 9. Print out the raw verification output strings received
                print("\n[Server Verification Test Output]:")
                print("-" * 50)
                for content_item in result.content:
                    # Content can be text or embedded objects, we pull the text element
                    if hasattr(content_item, 'text'):
                        print(content_item.text)
                    else:
                        print(content_item)
                print("-" * 50)
                print("\nSuccess! The custom LangChain DDG Proxy MCP server is functioning properly.")

    except Exception as e:
        print(f"\n[Test Failed] An error occurred while testing the server connection:")
        print(f"Error Details: {e}")

if __name__ == "__main__":
    # Execute the asynchronous test suite runner
    asyncio.run(run_mcp_test())
