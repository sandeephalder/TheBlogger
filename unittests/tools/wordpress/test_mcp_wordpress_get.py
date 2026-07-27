import asyncio
import os
import sys
import pytest
import httpx
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

load_dotenv()

from tools.wordpress_tool import list_recent_posts

# --- Pure Unit Tests ---

@patch("httpx.AsyncClient.get")
def test_list_recent_posts_success(mock_get):
    """Test listing recent posts with mocked HTTP response."""
    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = [
            {
                "title": {"rendered": "Test WordPress Post"},
                "link": "https://example.wordpress.com/test-post"
            }
        ]
        mock_get.return_value = mock_response

        response = await list_recent_posts(per_page=1)
        assert "- Title: Test WordPress Post" in response
        assert "Link: https://example.wordpress.com/test-post" in response

    asyncio.run(_run())


@patch("httpx.AsyncClient.get")
def test_list_recent_posts_empty(mock_get):
    """Test listing recent posts when no posts exist."""
    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        response = await list_recent_posts(per_page=5)
        assert response == "No posts found."

    asyncio.run(_run())


@patch("httpx.AsyncClient.get")
def test_list_recent_posts_http_error(mock_get):
    """Test handling of HTTPStatusError from WordPress REST API."""
    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        error = httpx.HTTPStatusError("401 Unauthorized", request=MagicMock(), response=mock_response)
        mock_get.side_effect = error

        response = await list_recent_posts(per_page=5)
        assert "WordPress API Error: Status 401 - Unauthorized" in response

    asyncio.run(_run())


@patch("httpx.AsyncClient.get")
def test_list_recent_posts_generic_exception(mock_get):
    """Test handling of unexpected generic exceptions."""
    async def _run():
        mock_get.side_effect = Exception("Connection refused")
        response = await list_recent_posts(per_page=5)
        assert "An unexpected error occurred: Connection refused" in response

    asyncio.run(_run())
