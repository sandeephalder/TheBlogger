from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    """
    State for the conversational agent.

    `add_messages` appends each turn to the running history instead of
    overwriting it, so the graph keeps the whole conversation.
    """
    messages: Annotated[list, add_messages]
