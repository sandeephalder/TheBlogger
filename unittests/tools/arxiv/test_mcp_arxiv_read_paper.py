import sys
import os
import datetime
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from tools.arxiv_tool import get_arxiv_paper_by_id

# --- Fixtures ---

@pytest.fixture
def mock_arxiv_paper():
    paper = MagicMock()
    paper.title = "Attention Is All You Need"
    paper.authors = [MagicMock(name="Ashish Vaswani"), MagicMock(name="Noam Shazeer")]
    paper.authors[0].name = "Ashish Vaswani"
    paper.authors[1].name = "Noam Shazeer"
    paper.published = datetime.datetime(2017, 6, 12)
    paper.primary_category = "cs.CL"
    paper.pdf_url = "https://arxiv.org/pdf/1706.03762"
    paper.summary = "The dominant sequence transduction models are based on complex recurrent..."
    return paper

# --- Pure Unit Tests ---

@patch("tools.arxiv_tool._download_and_extract_pdf")
@patch("tools.arxiv_tool.client.results")
def test_get_arxiv_paper_by_id_success(mock_results, mock_download, mock_arxiv_paper):
    """Test successfully retrieving a paper by its exact ID with mocks."""
    mock_results.return_value = iter([mock_arxiv_paper])
    mock_download.return_value = (
        "file:///Users/sandi-mac/Documents/Practice/TheBlogger/arxiv_cache/1706.03762.pdf",
        "--- Page 1 ---\nSample extracted full paper text..."
    )
    
    response = get_arxiv_paper_by_id("1706.03762")
    
    assert "Title: Attention Is All You Need" in response
    assert "ID: 1706.03762" in response
    assert "Authors: Ashish Vaswani, Noam Shazeer" in response
    assert "Published: 2017-06-12" in response
    assert "Primary Category: cs.CL" in response
    assert "Local PDF Link: file:///" in response
    assert "Full Abstract:" in response
    assert "Full Paper Text:\n--- Page 1 ---" in response

@patch("tools.arxiv_tool.client.results")
def test_get_arxiv_paper_by_id_not_found(mock_results):
    """Test the tool's behavior when arXiv returns no results for an ID."""
    mock_results.return_value = iter([])
    
    response = get_arxiv_paper_by_id("0000.00000")
    
    assert "Error: No arXiv paper found with ID '0000.00000'" in response

@patch("tools.arxiv_tool._download_and_extract_pdf")
@patch("tools.arxiv_tool.client.results")
def test_get_arxiv_paper_by_id_whitespace_handling(mock_results, mock_download, mock_arxiv_paper):
    """Test that the tool handles accidental whitespace added to IDs."""
    mock_results.return_value = iter([mock_arxiv_paper])
    mock_download.return_value = ("file:///dummy/path.pdf", "Extracted text")
    
    response = get_arxiv_paper_by_id("  1706.03762 \n")
    
    assert "ID: 1706.03762" in response


