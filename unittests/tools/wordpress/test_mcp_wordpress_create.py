import asyncio
import os
import sys
import pytest
import httpx
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

load_dotenv()

from tools.wordpress_tool import create_new_post

# --- Pure Unit Tests ---

@patch("httpx.AsyncClient.post")
def test_create_new_post_success_draft(mock_post):
    """Test creating a new draft post with mocked HTTP response."""
    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "id": 101,
            "status": "draft",
            "link": "https://example.wordpress.com/my-first-post"
        }
        mock_post.return_value = mock_response

        response = await create_new_post(title="New Post", content="Post content", status="draft")
        assert "🎉 Success! Post created successfully." in response
        assert "- ID: 101" in response
        assert "- Status: DRAFT" in response

    asyncio.run(_run())


@patch("httpx.AsyncClient.post")
def test_create_new_post_success_publish(mock_post):
    """Test creating and publishing a post directly."""
    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "id": 102,
            "status": "publish",
            "link": "https://example.wordpress.com/live-post"
        }
        mock_post.return_value = mock_response

        response = await create_new_post(title="Live Post", content="Live content", status="publish")
        assert "🎉 Success! Post created successfully." in response
        assert "- ID: 102" in response
        assert "- Status: PUBLISH" in response

    asyncio.run(_run())


@patch("httpx.AsyncClient.post")
def test_create_new_post_http_error(mock_post):
    """Test handling of HTTP error during post creation."""
    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        error = httpx.HTTPStatusError("400 Bad Request", request=MagicMock(), response=mock_response)
        mock_post.side_effect = error

        response = await create_new_post(title="Fail Post", content="Content")
        assert "WordPress API Error: Status 400 - Bad Request" in response

    asyncio.run(_run())


@patch("httpx.AsyncClient.post")
def test_create_new_post_generic_exception(mock_post):
    """Test handling of generic exception during post creation."""
    async def _run():
        mock_post.side_effect = Exception("Timeout error")
        response = await create_new_post(title="Timeout Post", content="Content")
        assert "An unexpected error occurred: Timeout error" in response

    asyncio.run(_run())
