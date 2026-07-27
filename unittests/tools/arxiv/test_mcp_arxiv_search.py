import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from tools.arxiv_tool import search_arxiv_papers

# --- Pure Unit Tests ---

@patch("tools.arxiv_tool.client.results")
def test_search_arxiv_papers_success(mock_results):
    """Test searching arXiv papers with mocked client response."""
    paper = MagicMock()
    paper.entry_id = "http://arxiv.org/abs/1706.03762v7"
    paper.title = "Attention Is All You Need"
    paper.authors = [MagicMock(name="Ashish Vaswani")]
    paper.authors[0].name = "Ashish Vaswani"
    paper.published = MagicMock()
    paper.published.strftime.return_value = "2017-06-12"
    paper.pdf_url = "https://arxiv.org/pdf/1706.03762"
    paper.summary = "The dominant sequence transduction models..."
    
    mock_results.return_value = iter([paper])
    
    response = search_arxiv_papers(query="Attention Is All You Need", max_results=1)
    
    assert "Title: Attention Is All You Need" in response
    assert "ID: 1706.03762" in response
    assert "Authors: Ashish Vaswani" in response
    assert "Published: 2017-06-12" in response
    assert "PDF Link: https://arxiv.org/pdf/1706.03762" in response

@patch("tools.arxiv_tool.client.results")
def test_search_arxiv_papers_no_results(mock_results):
    """Test searching arXiv when no papers match query."""
    mock_results.return_value = iter([])
    response = search_arxiv_papers(query="NonExistentPaperQueryXYZ123")
    assert response == "No papers found matching that query."

@patch("tools.arxiv_tool.client.results")
def test_search_arxiv_papers_entry_id_parsing(mock_results):
    """Test correctly parsing entry_id into paper ID."""
    paper = MagicMock()
    paper.entry_id = "http://arxiv.org/abs/2301.00001v3"
    paper.title = "Sample Paper"
    paper.authors = [MagicMock(name="John Doe")]
    paper.authors[0].name = "John Doe"
    paper.published = MagicMock()
    paper.published.strftime.return_value = "2023-01-01"
    paper.pdf_url = "https://arxiv.org/pdf/2301.00001"
    paper.summary = "Sample summary."
    
    mock_results.return_value = iter([paper])
    response = search_arxiv_papers(query="Sample")
    
    assert "ID: 2301.00001" in response

@patch("tools.arxiv_tool.client.results")
def test_search_arxiv_papers_multiple_results(mock_results):
    """Test formatting of multiple paper search results."""
    paper1 = MagicMock()
    paper1.entry_id = "http://arxiv.org/abs/1111.1111v1"
    paper1.title = "Paper One"
    paper1.authors = [MagicMock(name="Author One")]
    paper1.authors[0].name = "Author One"
    paper1.published = MagicMock()
    paper1.published.strftime.return_value = "2021-01-01"
    paper1.pdf_url = "https://arxiv.org/pdf/1111.1111"
    paper1.summary = "Summary 1"

    paper2 = MagicMock()
    paper2.entry_id = "http://arxiv.org/abs/2222.2222v1"
    paper2.title = "Paper Two"
    paper2.authors = [MagicMock(name="Author Two")]
    paper2.authors[0].name = "Author Two"
    paper2.published = MagicMock()
    paper2.published.strftime.return_value = "2022-02-02"
    paper2.pdf_url = "https://arxiv.org/pdf/2222.2222"
    paper2.summary = "Summary 2"

    mock_results.return_value = iter([paper1, paper2])
    response = search_arxiv_papers(query="Multiple", max_results=2)

    assert "Title: Paper One" in response
    assert "Title: Paper Two" in response
    assert "----------------------------------------" in response
