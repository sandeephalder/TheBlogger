import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from agents.research_tool_node import ResearchToolNode

def test_research_tool_node_init():
    """Test initialization of ResearchToolNode with arXiv tools."""
    mock_llm = MagicMock()
    mock_bound_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_bound_llm

    node_wrapper = ResearchToolNode(mock_llm)

    assert len(node_wrapper.langchain_tools) == 2
    assert "search_arxiv_papers" in node_wrapper.tool_map
    assert "get_arxiv_paper_by_id" in node_wrapper.tool_map
    mock_llm.bind_tools.assert_called_once_with(node_wrapper.langchain_tools)


def test_research_tool_node_execution_no_tools():
    """Test searchnode_execution when LLM does not return any tool calls."""
    mock_llm = MagicMock()
    mock_bound_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_bound_llm
    
    mock_response = MagicMock()
    mock_response.content = "ArXiv paper summary without tool calls"
    mock_response.tool_calls = []
    mock_bound_llm.invoke.return_value = mock_response

    node_wrapper = ResearchToolNode(mock_llm)
    state = {"topic": "GNN", "blog": {"title": "Graph Neural Networks Overview"}}
    
    result = node_wrapper.research_node_execution(state)
    assert result["blog"]["research_summary"] == "ArXiv paper summary without tool calls"
    assert result["blog"]["tool_calls"] == []


@patch("agents.research_tool_node.ResearchToolNode._execute_tool_call")
def test_research_tool_node_execution_with_tools(mock_execute_tool):
    """Test research_node_execution when LLM returns tool calls for arXiv search."""
    mock_llm = MagicMock()
    mock_bound_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_bound_llm
    
    mock_initial_response = MagicMock()
    mock_initial_response.content = ""
    mock_initial_response.tool_calls = [
        {"name": "search_arxiv_papers", "args": {"query": "Graph Neural Networks"}}
    ]
    mock_bound_llm.invoke.return_value = mock_initial_response

    mock_execute_tool.return_value = "Title: GNN Paper\nSummary: Deep learning on graphs."
    
    mock_final_response = MagicMock()
    mock_final_response.content = "Synthesized arXiv Paper Summary"
    mock_llm.invoke.return_value = mock_final_response

    node_wrapper = ResearchToolNode(mock_llm)
    state = {"topic": "GNN", "blog": {"title": "Graph Neural Networks Overview"}}
    
    result = node_wrapper.research_node_execution(state)
    
    mock_execute_tool.assert_called_once_with("search_arxiv_papers", {"query": "Graph Neural Networks"})
    assert result["blog"]["research_summary"] == "Synthesized arXiv Paper Summary"
