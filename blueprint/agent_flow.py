from agents.blog_node import BlogNode
from langgraph.graph import StateGraph, START, END
from blueprint.states.blogstate import BlogState
from utils.constants import LLM_PROVIDER_GEMINI
from llms.llm_factory import LLMFactory
from utils.constants import GEMINI_MODEL_FLASH,LLM_PROVIDER_GEMINI
from agents.duckduck_search_tool_node import SearchDuckDuckGoNode


class AgentFlow:
    def __init__(self,llm):
        self.llm=llm
        self.graph=StateGraph(BlogState)

    def build_topic_graph(self):
        """
        Build a graph for the blog node
        """

        self.blog_node_obj=BlogNode(self.llm)
        self.graph.add_node("question_breakdown",self.blog_node_obj.questions_breakdown)
        self.search_node_obj = SearchDuckDuckGoNode(self.llm)
        self.graph.add_node("search", self.search_node_obj.searchnode_execution)
        self.graph.add_node("blog_content_generation",self.blog_node_obj.blog_content_generation)

        ## Edges
        self.graph.add_edge(START,"question_breakdown")
        self.graph.add_edge("question_breakdown","search")
        self.graph.add_edge("search","blog_content_generation")
        self.graph.add_edge("blog_content_generation",END)  
        
        return self.graph


    def setup_blog_flow(self,area):
        if area == "blog":
            self.build_topic_graph()

        return self.graph.compile()


llm = LLMFactory().get_llm(LLM_PROVIDER_GEMINI, GEMINI_MODEL_FLASH)
agent_flow = AgentFlow(llm)
graph = agent_flow.setup_blog_flow("blog")


            

        

            

        