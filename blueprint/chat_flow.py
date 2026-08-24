from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agents.hindi_chat_node import HindiChatNode
from blueprint.states.chatstate import ChatState

class ChatFlow:
    """
    Builds the conversational graph.

    Kept separate from AgentFlow because the chat graph runs on ChatState
    (a growing message list) while the blog graph runs on BlogState.
    """

    def __init__(self, llm):
        self.llm = llm
        self.graph = StateGraph(ChatState)

    def build_hindi_chat_graph(self):
        """
        Build a single-node conversational graph that always replies in Hindi.
        """
        self.chat_node_obj = HindiChatNode(self.llm)

        # Nodes
        self.graph.add_node("hindi_chat", self.chat_node_obj.chat_node_execution)

        # Edges
        self.graph.add_edge(START, "hindi_chat")
        self.graph.add_edge("hindi_chat", END)

        return self.graph

    def setup_chat_flow(self, area="hindi", checkpointer=None):
        """
        Compile the chat graph. A checkpointer is what makes the agent
        multi-turn: pass a thread_id at invoke time and LangGraph replays
        that thread's history into the state.
        """
        if area == "hindi":
            self.build_hindi_chat_graph()
        else:
            raise ValueError(f"Invalid chat flow area : {area}")

        return self.graph.compile(checkpointer=checkpointer or MemorySaver())
