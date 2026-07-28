import sys
import os
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from agents.duckduck_search_tool_node import SearchDuckDuckGoNode

def test_searchnode_execution_no_tool_calls():
    """Test searchnode_execution when LLM returns content without requesting tool calls."""
    mock_llm = MagicMock()
    mock_bound_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_bound_llm

    mock_response = MagicMock()
    mock_response.content = '[{"title": "GNN Overview", "summary": "Ans1", "links": []}]'
    mock_response.tool_calls = []
    mock_bound_llm.invoke.return_value = mock_response

    node = SearchDuckDuckGoNode(llm=mock_llm)
    
    state = {
        "topic": "GNN",
        "blog": {"title": "Graph Neural Networks"}
    }
    
    result = node.searchnode_execution(state)
    
    assert "blog" in result
    assert result["blog"]["search_summary"] == '[{"title": "GNN Overview", "summary": "Ans1", "links": []}]'


@patch.object(SearchDuckDuckGoNode, "_execute_tool_call")
def test_searchnode_execution_with_tool_calls(mock_execute_tool):
    """Test searchnode_execution when LLM emits tool_calls and tools are executed."""
    mock_execute_tool.return_value = "[1] Graph Neural Networks Intro\nURL: https://example.com/gnn"

    mock_llm = MagicMock()
    mock_bound_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_bound_llm

    # Initial response with tool_calls
    mock_tool_response = MagicMock()
    mock_tool_response.content = ""
    mock_tool_response.tool_calls = [{"name": "ddg_web_search", "args": {"query": "GNN"}}]
    mock_bound_llm.invoke.return_value = mock_tool_response

    # Synthesis response from mock_llm
    mock_synthesis_response = MagicMock()
    mock_synthesis_response.content = "GNNs are deep learning models operating on graphs."
    mock_llm.invoke.return_value = mock_synthesis_response

    node = SearchDuckDuckGoNode(llm=mock_llm)

    state = {
        "topic": "GNN",
        "blog": {"title": "Graph Neural Networks"}
    }

    result = node.searchnode_execution(state)

    mock_execute_tool.assert_called_once_with("ddg_web_search", {"query": "GNN"})
    assert result["blog"]["search_summary"] == "GNNs are deep learning models operating on graphs."
