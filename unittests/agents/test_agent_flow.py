import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from blueprint.agent_flow import AgentFlow

def test_agent_flow_build_graph():
    """Test that AgentFlow correctly builds the graph with both search and research nodes."""
    mock_llm = MagicMock()
    mock_bound_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_bound_llm

    agent_flow = AgentFlow(mock_llm)
    graph = agent_flow.setup_blog_flow("blog")

    assert graph is not None
    # Verify graph contains expected nodes
    nodes = list(agent_flow.graph.nodes.keys())
    assert "question_breakdown" in nodes
    assert "search" in nodes
    assert "research" in nodes
    assert "blog_content_generation" in nodes
