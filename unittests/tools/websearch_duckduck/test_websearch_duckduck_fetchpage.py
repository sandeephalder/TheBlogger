import sys
import os
import asyncio
import pytest
import httpx
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from tools.websearch_duckduck import ddg_fetch_page

# --- Unit Tests for ddg_fetch_page ---

@patch("httpx.get")
def test_ddg_fetch_page_paragraphs_success(mock_get):
    """Test successfully fetching page content with paragraph tags."""
    async def _run():
        html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <header><h1>Header Navigation</h1></header>
                <nav><a href="#">Home</a></nav>
                <p>This is the first paragraph with main content.</p>
                <p>This is the second paragraph with additional details.</p>
                <script>console.log("ignore me");</script>
                <style>.ignore { color: red; }</style>
                <footer>Footer info</footer>
            </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = await ddg_fetch_page("https://example.com/test")
        assert "This is the first paragraph with main content." in result
        assert "This is the second paragraph with additional details." in result
        assert "Header Navigation" not in result
        assert "console.log" not in result
        assert "Footer info" not in result

    asyncio.run(_run())


@patch("httpx.get")
def test_ddg_fetch_page_fallback_no_paragraphs(mock_get):
    """Test fallback mechanism when page has no <p> tags."""
    async def _run():
        html_content = """
        <html>
            <body>
                <div>Semantic content without paragraph tags.</div>
                <span>More plain body text.</span>
            </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = await ddg_fetch_page("https://example.com/noparagraphs")
        assert "Semantic content without paragraph tags." in result
        assert "More plain body text." in result

    asyncio.run(_run())


@patch("httpx.get")
def test_ddg_fetch_page_http_error(mock_get):
    """Test handling of HTTPStatusError when fetching web page."""
    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        error = httpx.HTTPStatusError("404 Not Found", request=MagicMock(), response=mock_response)
        mock_get.side_effect = error

        result = await ddg_fetch_page("https://example.com/404")
        assert "Error fetching target web page: 404 Not Found" in result

    asyncio.run(_run())


@patch("httpx.get")
def test_ddg_fetch_page_generic_exception(mock_get):
    """Test handling of generic connection or timeout error."""
    async def _run():
        mock_get.side_effect = Exception("Connection timeout")

        result = await ddg_fetch_page("https://example.com/timeout")
        assert "Error fetching target web page: Connection timeout" in result

    asyncio.run(_run())
