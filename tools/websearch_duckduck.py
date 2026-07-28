from utils.colors import print_cyan
import sys
import asyncio
from functools import partial
from mcp.server.fastmcp import FastMCP
from duckduckgo_search import DDGS
import httpx
from bs4 import BeautifulSoup

# Initialize FastMCP Server natively
mcp = FastMCP("Custom LangChain DDG Proxy")

def log_info(message: str):
    """Safely print logging information to stderr so it does not corrupt the JSON-RPC stdout pipeline."""
    sys.stderr.write(f"[Server Log] {message}\n")
    sys.stderr.flush()

@mcp.tool()
async def ddg_web_search(query: str) -> str:
    """
    Search the web anonymously via DuckDuckGo to get structured summaries and links.
    """
    print(" inside ddg web search node\n\n===============> ", query)
    log_info(f"Received web search request for: '{query}'")
    try:
        loop = asyncio.get_running_loop()
        def execute_search():
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                print_cyan(f"DDG Search Results : \n==============> \n",results)
                if not results: return "No results found."
                return "\n".join([f"[{i}] {r.get('title')}\nURL: {r.get('href')}\nSummary: {r.get('body')}\n" for i, r in enumerate(results, 1)])
        return await loop.run_in_executor(None, execute_search)
    except Exception as e:
        return f"Error executing DuckDuckGo search: {str(e)}"


@mcp.tool()
async def ddg_fetch_page(url: str) -> str:
    """
    Fetch and extract clean text content from a specific web page URL.
    
    Args:
        url: The web page address (HTTP/HTTPS) to extract text from.
    """
    print(" inside ddg fetch page node\n\n===============> ", url)
    log_info(f"Received page fetch request for URL: '{url}'")
    
    try:
        loop = asyncio.get_running_loop()
        
        def execute_fetch():
            # Send an HTTP GET request with a standard browser User-Agent header
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
            response = httpx.get(url, headers=headers, timeout=10.0, follow_redirects=True)
            response.raise_for_status()
            
            # Parse the HTML structure and extract human-readable text strings
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Strip away non-content structural elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
                
            # Grab remaining clean paragraph blocks
            paragraphs = [p.get_text().strip() for p in soup.find_all("p") if p.get_text().strip()]
            
            if not paragraphs:
                # Fallback if page doesn't use standard semantic paragraph structures
                return soup.get_text(separator="\n", strip=True)[:3000]
                
            return "\n\n".join(paragraphs)[:4000]  # Limit characters to fit LLM window sizes cleanly

        results_text = await loop.run_in_executor(None, execute_fetch)
        return results_text

    except Exception as e:
        log_info(f"Exception during page fetch: {str(e)}")
        return f"Error fetching target web page: {str(e)}"

if __name__ == "__main__":
    mcp.run()
