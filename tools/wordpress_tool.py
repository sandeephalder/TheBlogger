import os
from dotenv import load_dotenv
import httpx
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

WP_URL = os.getenv("WORDPRESS_URL").rstrip("/")
WP_USER = os.getenv("WORDPRESS_USERNAME")
WP_PASSWORD = os.getenv("WORDPRESS_PASSWORD")

# Initialize FastMCP Server
mcp = FastMCP("WordPress-Test-Server")

@mcp.tool()
async def edit_post(post_id: int, title: str = None, content: str = None, status: str = None) -> str:
    """
    Edits an existing post on the WordPress.com blog using its ID.
    
    Args:
        post_id: The ID of the post to update.
        title: Optional new title.
        content: Optional new body content.
        status: Optional new status (e.g., "publish", "draft").
    """
    auth = (WP_USER, WP_PASSWORD)
    # Endpoint targets the specific post ID
    endpoint = f"{WP_URL}/wp-json/wp/v2/posts/{post_id}"
    
    # Build payload containing only the fields you want to update
    payload = {}
    if title: payload["title"] = title
    if content: payload["content"] = content
    if status: payload["status"] = status
        
    if not payload:
        return "No updates were provided. Please provide a title, content, or status to change."

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(endpoint, auth=auth, json=payload, follow_redirects=True)
            response.raise_for_status()
            post_data = response.json()
            return f"🔄 Post {post_id} updated successfully!\n- Title: {post_data.get('title', {}).get('rendered')}\n- Status: {post_data.get('status').upper()}"
        except httpx.HTTPStatusError as e:
            return f"WordPress API Error: Status {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"


@mcp.tool()
async def delete_post(post_id: int, force: bool = False) -> str:
    """
    Deletes a post from the WordPress.com blog using its ID.
    
    Args:
        post_id: The ID of the post to delete.
        force: If False (default), moves post to Trash. If True, permanently deletes it.
    """
    auth = (WP_USER, WP_PASSWORD)
    # Endpoint targets the specific post ID
    endpoint = f"{WP_URL}/wp-json/wp/v2/posts/{post_id}"
    
    async with httpx.AsyncClient() as client:
        try:
            # Use client.delete for removal requests
            response = await client.delete(
                endpoint, 
                auth=auth, 
                params={"force": "true" if force else "false"},
                follow_redirects=True
            )
            response.raise_for_status()
            
            action = "permanently deleted" if force else "moved to Trash"
            return f"🗑️ Success! Post {post_id} has been {action}."
        except httpx.HTTPStatusError as e:
            return f"WordPress API Error: Status {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"



@mcp.tool()
async def create_new_post(title: str, content: str, status: str = "draft") -> str:
    """
    Creates and publishes a new post to the WordPress.com blog.
    
    Args:
        title: The title of the post.
        content: The body content of the post (HTML or plain text).
        status: The publishing status. Use "draft" to review first, or "publish" to go live instantly.
    """
    auth = (WP_USER, WP_PASSWORD)
    
    # Clean the domain string for the WordPress.com API format
    endpoint = f"{WP_URL}/wp-json/wp/v2/posts"
    
    # Data payload required by the WordPress REST API
    payload = {
        "title": title,
        "content": content,
        "status": status
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Use client.post for sending data packets
            response = await client.post(
                endpoint,
                auth=auth,
                json=payload,
                follow_redirects=True
            )
            response.raise_for_status()
            post_data = response.json()
            
            return f"🎉 Success! Post created successfully.\n- ID: {post_data.get('id')}\n- Status: {post_data.get('status').upper()}\n- Link: {post_data.get('link')}"
            
        except httpx.HTTPStatusError as e:
            return f"WordPress API Error: Status {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

import logging

# 1. Set up a safe logger at the top of your file
logger = logging.getLogger("wp_mcp")

@mcp.tool()
async def list_recent_posts(per_page: int = 5) -> str:
    """
    Fetches the most recent posts from the WordPress site.
    
    Args:
        per_page: Number of posts to retrieve (default is 5).
    """
    auth = (WP_USER, WP_PASSWORD)
    
    # 2. Use logger.info instead of print() 🔐
    logger.info(f"URL: {WP_URL}")
    logger.info(f"User: {WP_USER}")
    
    endpoint = f"{WP_URL}/wp-json/wp/v2/posts"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                endpoint, 
                auth=auth, 
                params={"per_page": per_page, "status": "publish"},
                follow_redirects=True
            )
            response.raise_for_status()
            
            # 3. Use logger.info instead of print() 📝
            logger.info(f"Response Status: {response.status_code}")
            posts = response.json()
            
            if not posts:
                logger.info("No posts found.")
                return "No posts found."
                
            output = []
            for post in posts:
                output.append(f"- Title: {post['title']['rendered']}\n  Link: {post['link']}")
            return "\n".join(output)
            
        except httpx.HTTPStatusError as e:
            return f"WordPress API Error: Status {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"


if __name__ == "__main__":
    # Run using the default stdio transport layer for LLM clients
    mcp.run(transport="stdio")
