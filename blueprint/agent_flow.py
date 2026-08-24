from agents.blog_node import BlogNode
from agents.duckduck_search_tool_node import SearchDuckDuckGoNode
from agents.research_tool_node import ResearchToolNode
from langgraph.graph import StateGraph, START, END
from blueprint.states.blogstate import BlogState
from utils.constants import GEMINI_MODEL_FLASH, LLM_PROVIDER_GEMINI
from llms.llm_factory import LLMFactory

class AgentFlow:
    def __init__(self, llm):
        self.llm = llm
        self.graph = StateGraph(BlogState)

    def build_topic_graph(self):
        """
        Build a graph for the blog node incorporating both web search and academic paper research tools
        """
        self.blog_node_obj = BlogNode(self.llm)
        self.search_node_obj = SearchDuckDuckGoNode(self.llm)
        self.research_node_obj = ResearchToolNode(self.llm)

        # Nodes
        self.graph.add_node("question_breakdown", self.blog_node_obj.questions_breakdown)
        self.graph.add_node("search", self.search_node_obj.searchnode_execution)
        self.graph.add_node("research", self.research_node_obj.research_node_execution)
        self.graph.add_node("blog_content_generation", self.blog_node_obj.blog_content_generation)

        # Edges
        self.graph.add_edge(START, "question_breakdown")
        self.graph.add_edge("question_breakdown", "search")
        self.graph.add_edge("search", "research")
        self.graph.add_edge("research", "blog_content_generation")
        self.graph.add_edge("blog_content_generation", END)  
        
        return self.graph

    def setup_blog_flow(self, area):
        if area == "blog":
            self.build_topic_graph()

        return self.graph.compile()

# `graph` is what langgraph-cli picks up. Building it needs a live Gemini key,
# so keep a missing key from breaking every import of this module (app.py imports
# it for the /blogs route, and the chat flow lives alongside it).
try:
    llm = LLMFactory().get_llm(LLM_PROVIDER_GEMINI, GEMINI_MODEL_FLASH)
    agent_flow = AgentFlow(llm)
    graph = agent_flow.setup_blog_flow("blog")
except Exception as e:
    print(f"Skipping default blog graph build : {e}")
    llm = None
    agent_flow = None
    graph = None