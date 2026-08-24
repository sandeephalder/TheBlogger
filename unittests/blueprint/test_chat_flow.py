import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_core.messages import AIMessage, HumanMessage

from blueprint.chat_flow import ChatFlow

def test_chat_flow_builds_hindi_graph():
    """The compiled chat graph exposes the hindi_chat node."""
    mock_llm = MagicMock()

    chat_flow = ChatFlow(mock_llm)
    graph = chat_flow.setup_chat_flow("hindi")

    assert graph is not None
    assert "hindi_chat" in list(chat_flow.graph.nodes.keys())


def test_chat_flow_rejects_unknown_area():
    """An unknown flow name fails loudly instead of compiling an empty graph."""
    with pytest.raises(ValueError):
        ChatFlow(MagicMock()).setup_chat_flow("marathi")


def test_chat_flow_remembers_thread_across_turns():
    """The checkpointer carries history from one invoke to the next on a thread."""
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = [
        AIMessage(content="दिल्ली।"),
        AIMessage(content="वहाँ गर्मियाँ तेज़ होती हैं।"),
    ]

    graph = ChatFlow(mock_llm).setup_chat_flow("hindi")
    config = {"configurable": {"thread_id": "test-thread"}}

    graph.invoke({"messages": [HumanMessage(content="भारत की राजधानी क्या है?")]}, config=config)
    state = graph.invoke({"messages": [HumanMessage(content="वहाँ का मौसम कैसा है?")]}, config=config)

    # first question, first answer, follow-up question, follow-up answer
    assert len(state["messages"]) == 4
    second_call_messages = mock_llm.invoke.call_args_list[1][0][0]
    assert second_call_messages[1].content == "भारत की राजधानी क्या है?"


def test_chat_flow_isolates_threads():
    """Two thread ids do not share memory."""
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="ठीक है।")

    graph = ChatFlow(mock_llm).setup_chat_flow("hindi")

    graph.invoke({"messages": [HumanMessage(content="पहला सवाल")]},
                 config={"configurable": {"thread_id": "thread-a"}})
    state_b = graph.invoke({"messages": [HumanMessage(content="दूसरा सवाल")]},
                           config={"configurable": {"thread_id": "thread-b"}})

    assert len(state_b["messages"]) == 2
    assert state_b["messages"][0].content == "दूसरा सवाल"
