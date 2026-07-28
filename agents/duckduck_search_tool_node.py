import sys
import asyncio
from typing import List, Dict, Any
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode
from tools.websearch_duckduck import ddg_web_search, ddg_fetch_page
from blueprint.states.blogstate import BlogState
from prompts.search_node_prompt import search_prompt
from utils.colors import print_yellow, print_magenta, print_cyan, print_blue, print_green

def log_tool_node(text: str):
    """Safely log debug info to stderr to protect the Stdio streams."""
    sys.stderr.write(f"[Tool Node Log] {text}\n")
    sys.stderr.flush()

class SearchDuckDuckGoNode:
    """Encapsulates LangGraph tool nodes and custom manual execution logic."""
    def __init__(self, llm):
        # Initialize LLM
        self.llm = llm
        # 1. Build the automatic routing ToolNode
        self.langchain_tools = [ddg_web_search, ddg_fetch_page]
        self.llm_with_tools = self.llm.bind_tools(self.langchain_tools)
        self.node = ToolNode(self.langchain_tools)
        
        # 2. Cache a tool map to allow easy manual calls by name
        self.tool_map: Dict[str, Any] = {getattr(t, "name", getattr(t, "__name__", str(t))): t for t in self.langchain_tools}
        
    def get_tool(self, name: str):
        """Helper to extract a specific tool instance safely."""
        return self.tool_map.get(name)

    def _execute_tool_call(self, tool_name: str, args: dict) -> str:
        """Executes the matching tool function safely."""
        tool_func = self.get_tool(tool_name)
        if not tool_func:
            log_tool_node(f"Warning: Tool '{tool_name}' not found.")
            return f"Tool '{tool_name}' not found."
            
        fn = getattr(tool_func, "fn", tool_func)
        if asyncio.iscoroutinefunction(fn):
            try:
                return asyncio.run(fn(**args))
            except RuntimeError:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(fn(**args))
        elif hasattr(tool_func, "invoke"):
            return str(tool_func.invoke(args))
        elif callable(fn):
            return str(fn(**args))
        return str(tool_func)

    def searchnode_execution(self, state: BlogState):
        """
        Executes the search node for the given state using LLM bound with tools
        """
        print_yellow(f"\n🔎 Inside Search Node\n ===============> \nTopic: {state['topic']}")

        blog_data = state.get("blog", {})
        title_val = blog_data.get("title", "") if isinstance(blog_data, dict) else getattr(blog_data, "title", "")
        if not title_val:
            title_val = state.get("title", state.get("topic", ""))

        system_message = search_prompt.format(topic=state["topic"], title=title_val)

        if "topic" in state and state["topic"]:
            print_blue(f"System Message:\n{system_message}")
            response = self.llm_with_tools.invoke(system_message)
            print_cyan(f"LLM Response:\n{response}")
            
            search_summary = response.content
            tool_calls = getattr(response, "tool_calls", [])

            # Automatically execute tool calls if LLM requests search execution
            if tool_calls:
                print_magenta(f"\n⚙️  [Tool Node] Executing {len(tool_calls)} requested tool call(s)...")
                executed_results = []
                for tool_call in tool_calls:
                    t_name = tool_call.get("name")
                    t_args = tool_call.get("args", {})
                    print_green(f" -> Invoking tool '{t_name}' with args: {t_args}")
                    t_output = self._execute_tool_call(t_name, t_args)
                    executed_results.append(t_output)
                
                search_summary = "\n\n".join(executed_results)
                
                # Request final summary from LLM using retrieved tool results
                synthesis_prompt = f"{system_message}\n\nRetrieved Search Information:\n{search_summary}\n\nSummarize the factual key findings with links."
                final_response = self.llm.invoke(synthesis_prompt)
                if final_response.content:
                    search_summary = final_response.content

            return {
                "blog": {
                    "title": title_val,
                    "search_summary": search_summary,
                    "tool_calls": tool_calls
                }
            }
