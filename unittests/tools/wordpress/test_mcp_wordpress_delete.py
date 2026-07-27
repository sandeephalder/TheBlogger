import asyncio
import os
import sys
import pytest
import httpx
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

load_dotenv()

from tools.wordpress_tool import delete_post

# --- Pure Unit Tests ---

@patch("httpx.AsyncClient.delete")
def test_delete_post_trash_success(mock_delete):
    """Test moving post to Trash with mocked HTTP response."""
    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_delete.return_value = mock_response

        response = await delete_post(post_id=55, force=False)
        assert "🗑️ Success! Post 55 has been moved to Trash." in response

    asyncio.run(_run())


@patch("httpx.AsyncClient.delete")
def test_delete_post_force_success(mock_delete):
    """Test permanently deleting post with mocked HTTP response."""
    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_delete.return_value = mock_response

        response = await delete_post(post_id=55, force=True)
        assert "🗑️ Success! Post 55 has been permanently deleted." in response

    asyncio.run(_run())


@patch("httpx.AsyncClient.delete")
def test_delete_post_http_error(mock_delete):
    """Test handling of HTTP error during post deletion."""
    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Post Not Found"
        error = httpx.HTTPStatusError("404 Not Found", request=MagicMock(), response=mock_response)
        mock_delete.side_effect = error

        response = await delete_post(post_id=999)
        assert "WordPress API Error: Status 404 - Post Not Found" in response

    asyncio.run(_run())


@patch("httpx.AsyncClient.delete")
def test_delete_post_generic_exception(mock_delete):
    """Test handling of generic exception during post deletion."""
    async def _run():
        mock_delete.side_effect = Exception("Network unreachable")
        response = await delete_post(post_id=55)
        assert "An unexpected error occurred: Network unreachable" in response

    asyncio.run(_run())
