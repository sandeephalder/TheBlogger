import sys
import os
import asyncio
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from tools.websearch_duckduck import ddg_web_search, log_info

# --- Unit Tests for ddg_web_search and log_info ---

def test_log_info(capsys):
    """Test that log_info writes formatted log message to stderr."""
    log_info("Test log message")
    captured = capsys.readouterr()
    assert "[Server Log] Test log message\n" in captured.err


@patch("tools.websearch_duckduck.DDGS")
def test_ddg_web_search_success(mock_ddgs_cls):
    """Test successful DuckDuckGo web search returning formatted results."""
    async def _run():
        mock_ddgs_instance = MagicMock()
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs_instance
        mock_ddgs_instance.text.return_value = [
            {
                "title": "Python Programming Language",
                "href": "https://www.python.org",
                "body": "Python is a high-level programming language."
            },
            {
                "title": "DuckDuckGo Search",
                "href": "https://duckduckgo.com",
                "body": "Privacy-focused web search engine."
            }
        ]

        result = await ddg_web_search("Python")
        assert "[1] Python Programming Language" in result
        assert "URL: https://www.python.org" in result
        assert "Summary: Python is a high-level programming language." in result
        assert "[2] DuckDuckGo Search" in result

    asyncio.run(_run())


@patch("tools.websearch_duckduck.DDGS")
def test_ddg_web_search_no_results(mock_ddgs_cls):
    """Test web search when DuckDuckGo returns no results."""
    async def _run():
        mock_ddgs_instance = MagicMock()
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs_instance
        mock_ddgs_instance.text.return_value = []

        result = await ddg_web_search("NonExistentSearchQueryXYZ12345")
        assert result == "No results found."

    asyncio.run(_run())


@patch("tools.websearch_duckduck.DDGS")
def test_ddg_web_search_exception(mock_ddgs_cls):
    """Test handling of unexpected exception during web search."""
    async def _run():
        mock_ddgs_instance = MagicMock()
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs_instance
        mock_ddgs_instance.text.side_effect = Exception("Rate limit exceeded")

        result = await ddg_web_search("Python")
        assert "Error executing DuckDuckGo search: Rate limit exceeded" in result

    asyncio.run(_run())
