from langchain_core.messages import SystemMessage

from blueprint.states.chatstate import ChatState
from prompts.hindi_chat_prompt import hindi_chat_prompt
from utils.constants import HINDI_CHAT_HISTORY_WINDOW
from utils.colors import print_cyan, print_green, print_yellow

class HindiChatNode:
    """
    A class to represent the Hindi conversational node.

    The node is stateless by itself — the conversation history lives in the
    graph state and the checkpointer, so the same node serves every turn.
    """

    def __init__(self, llm, history_window=HINDI_CHAT_HISTORY_WINDOW):
        self.llm = llm
        self.history_window = history_window

    def _windowed_history(self, messages):
        """
        Keep only the most recent turns so the prompt does not grow without bound
        across a long conversation.
        """
        if self.history_window and len(messages) > self.history_window:
            return messages[-self.history_window:]
        return messages

    def chat_node_execution(self, state: ChatState):
        """
        Answer the latest user message in Hindi, using the conversation so far.
        """
        messages = state.get("messages", [])
        if not messages:
            print_yellow("\n⚠️  Hindi Chat Node called with no messages, skipping.")
            return {"messages": []}

        print_cyan(f"\n💬 Inside Hindi Chat Node\n ===============> \nUser: {messages[-1].content}")

        history = self._windowed_history(messages)
        conversation = [SystemMessage(content=hindi_chat_prompt)] + history
        response = self.llm.invoke(conversation)

        print_green(f"\n🗣️  सहायक:\n ===============> \n{response.content}")
        return {"messages": [response]}
