import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agents.hindi_chat_node import HindiChatNode
from prompts.hindi_chat_prompt import hindi_chat_prompt

def test_hindi_chat_node_prepends_hindi_system_prompt():
    """The Hindi system prompt must lead every call, ahead of the conversation."""
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="नमस्ते! मैं आपकी क्या मदद कर सकता हूँ?")

    node = HindiChatNode(mock_llm)
    state = {"messages": [HumanMessage(content="hello")]}

    result = node.chat_node_execution(state)

    sent_messages = mock_llm.invoke.call_args[0][0]
    assert isinstance(sent_messages[0], SystemMessage)
    assert sent_messages[0].content == hindi_chat_prompt
    assert sent_messages[1].content == "hello"
    assert result["messages"][0].content == "नमस्ते! मैं आपकी क्या मदद कर सकता हूँ?"


def test_hindi_chat_node_keeps_conversation_history():
    """Earlier turns are replayed so the model can resolve follow-up questions."""
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="दिल्ली भारत की राजधानी है।")

    node = HindiChatNode(mock_llm)
    state = {
        "messages": [
            HumanMessage(content="भारत की राजधानी क्या है?"),
            AIMessage(content="दिल्ली।"),
            HumanMessage(content="वहाँ का मौसम कैसा रहता है?"),
        ]
    }

    node.chat_node_execution(state)

    sent_messages = mock_llm.invoke.call_args[0][0]
    # system prompt + the three conversation turns
    assert len(sent_messages) == 4
    assert sent_messages[-1].content == "वहाँ का मौसम कैसा रहता है?"


def test_hindi_chat_node_windows_long_history():
    """Only the most recent turns are sent once the window is exceeded."""
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="ठीक है।")

    node = HindiChatNode(mock_llm, history_window=4)
    state = {"messages": [HumanMessage(content=f"सवाल {i}") for i in range(10)]}

    node.chat_node_execution(state)

    sent_messages = mock_llm.invoke.call_args[0][0]
    assert len(sent_messages) == 5  # system prompt + last 4 turns
    assert sent_messages[1].content == "सवाल 6"
    assert sent_messages[-1].content == "सवाल 9"


def test_hindi_chat_node_handles_empty_state():
    """An empty state is a no-op rather than a crash."""
    mock_llm = MagicMock()

    node = HindiChatNode(mock_llm)
    result = node.chat_node_execution({"messages": []})

    assert result == {"messages": []}
    mock_llm.invoke.assert_not_called()
