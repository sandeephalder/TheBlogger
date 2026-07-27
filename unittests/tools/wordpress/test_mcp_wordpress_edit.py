import asyncio
import os
import sys
import pytest
import httpx
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

load_dotenv()

from tools.wordpress_tool import edit_post

# --- Pure Unit Tests ---

@patch("httpx.AsyncClient.post")
def test_edit_post_success_title_and_status(mock_post):
    """Test editing title and status of an existing post."""
    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "id": 55,
            "title": {"rendered": "Updated Title"},
            "status": "publish"
        }
        mock_post.return_value = mock_response

        response = await edit_post(post_id=55, title="Updated Title", status="publish")
        assert "🔄 Post 55 updated successfully!" in response
        assert "- Title: Updated Title" in response
        assert "- Status: PUBLISH" in response

    asyncio.run(_run())


@patch("httpx.AsyncClient.post")
def test_edit_post_success_content(mock_post):
    """Test editing content only of an existing post."""
    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "id": 55,
            "title": {"rendered": "Existing Title"},
            "status": "draft"
        }
        mock_post.return_value = mock_response

        response = await edit_post(post_id=55, content="Updated Content Body")
        assert "🔄 Post 55 updated successfully!" in response

    asyncio.run(_run())


@patch("httpx.AsyncClient.post")
def test_edit_post_no_updates(mock_post):
    """Test calling edit_post with no update fields provided."""
    async def _run():
        response = await edit_post(post_id=55)
        assert "No updates were provided" in response

    asyncio.run(_run())


@patch("httpx.AsyncClient.post")
def test_edit_post_http_error(mock_post):
    """Test handling of HTTP error during post update."""
    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Post Not Found"
        error = httpx.HTTPStatusError("404 Not Found", request=MagicMock(), response=mock_response)
        mock_post.side_effect = error

        response = await edit_post(post_id=999, title="Non-existent")
        assert "WordPress API Error: Status 404 - Post Not Found" in response

    asyncio.run(_run())


@patch("httpx.AsyncClient.post")
def test_edit_post_generic_exception(mock_post):
    """Test handling of generic exception during post update."""
    async def _run():
        mock_post.side_effect = Exception("SSL Verification error")
        response = await edit_post(post_id=55, title="Title")
        assert "An unexpected error occurred: SSL Verification error" in response

    asyncio.run(_run())
