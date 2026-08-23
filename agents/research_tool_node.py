import sys
import asyncio
from typing import List, Dict, Any
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode
from tools.arxiv_tool import search_arxiv_papers, get_arxiv_paper_by_id
from blueprint.states.blogstate import BlogState
from prompts.research_node_prompt import research_prompt
from utils.colors import print_yellow, print_magenta, print_cyan, print_blue, print_green

def log_tool_node(text: str):
    """Safely log debug info to stderr to protect the Stdio streams."""
    sys.stderr.write(f"[Tool Node Log] {text}\n")
    sys.stderr.flush()

class ResearchToolNode:
    """Encapsulates LangGraph tool nodes for arXiv academic paper research."""
    def __init__(self, llm):
        self.llm = llm
        # Build the automatic routing ToolNode with ArXiv research tools
        self.langchain_tools = [search_arxiv_papers, get_arxiv_paper_by_id]
        self.llm_with_tools = self.llm.bind_tools(self.langchain_tools)
        self.node = ToolNode(self.langchain_tools)
        
        # Cache a tool map to allow easy manual calls by name
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
        import inspect
        try:
            sig = inspect.signature(fn) if callable(fn) else None
            if sig:
                valid_params = set(sig.parameters.keys())
                has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
                filtered_args = args if has_kwargs else {k: v for k, v in args.items() if k in valid_params}
            else:
                filtered_args = args
        except Exception:
            filtered_args = args

        if asyncio.iscoroutinefunction(fn):
            try:
                return asyncio.run(fn(**filtered_args))
            except RuntimeError:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(fn(**filtered_args))
        elif hasattr(tool_func, "invoke"):
            return str(tool_func.invoke(filtered_args))
        elif callable(fn):
            return str(fn(**filtered_args))
        return str(tool_func)

    def research_node_execution(self, state: BlogState):
        """
        Executes the research node for the given state using LLM bound with arXiv tools.
        """
        print_yellow(f"\n📚 Inside ArXiv Research Node\n ===============> \nTopic: {state['topic']}")

        blog_data = state.get("blog", {})
        title_val = blog_data.get("title", "") if isinstance(blog_data, dict) else getattr(blog_data, "title", "")
        if not title_val:
            title_val = state.get("title", state.get("topic", ""))

        system_message = research_prompt.format(topic=state["topic"], title=title_val)

        if "topic" in state and state["topic"]:
            print_blue(f"System Message:\n{system_message}")
            response = self.llm_with_tools.invoke(system_message)
            print_cyan(f"LLM Response:\n{response}")
            
            search_summary = response.content
            tool_calls = getattr(response, "tool_calls", [])

            # Automatically execute tool calls if LLM requests arXiv paper search/retrieval
            if tool_calls:
                print_magenta(f"\n⚙️  [Tool Node] Executing {len(tool_calls)} requested arXiv tool call(s)...")
                executed_results = []
                for tool_call in tool_calls:
                    t_name = tool_call.get("name")
                    t_args = tool_call.get("args", {})
                    print_green(f" -> Invoking tool '{t_name}' with args: {t_args}")
                    t_output = self._execute_tool_call(t_name, t_args)
                    executed_results.append(t_output)
                
                search_summary = "\n\n".join(executed_results)
                
                # Request final summary from LLM using retrieved arXiv research results
                synthesis_prompt = f"{system_message}\n\nRetrieved arXiv Research Information:\n{search_summary}\n\nSummarize key research paper findings with citations and IDs."
                final_response = self.llm.invoke(synthesis_prompt)
                if final_response.content:
                    search_summary = final_response.content

            return {
                "blog": {
                    "title": title_val,
                    "research_summary": search_summary,
                    "tool_calls": tool_calls
                }
            }

    # Alias for method compatibility
    searchnode_execution = research_node_execution
