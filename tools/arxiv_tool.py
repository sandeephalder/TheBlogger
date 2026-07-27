"""
{
  "mcpServers": {
    "arxiv-assistant": {
      "command": "uv",
      "args": [
        "run",
        "--with", "arxiv",
        "--with", "mcp",
        "path/to/your/arxiv_mcp.py"
      ]
    }
  }
}
"""

import urllib.request
from urllib.parse import urlparse
import os
import re
from mcp.server.fastmcp import FastMCP
import arxiv
import fitz

# --- MANDATORY HTTPS MONKEY PATCH FOR ARXIV ---
_original_init = urllib.request.Request.__init__

def forced_https_init(self, url, *args, **kwargs):
    if isinstance(url, str) and url.startswith("http://"):
        url = url.replace("http://", "https://", 1)
    elif hasattr(url, "geturl"):
        parsed = urlparse(url.geturl())
        if parsed.scheme == "http":
            url = parsed._replace(scheme="https").geturl()
    _original_init(self, url, *args, **kwargs)

urllib.request.Request.__init__ = forced_https_init
# ---------------------------------------------

# Initialize the FastMCP Server
mcp = FastMCP("arXiv Research Assistant")
client = arxiv.Client()
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../arxiv_cache"))

def _clean_text(raw_text: str) -> str:
    """Strip XML/HTML tags, non-printable & non-standard characters, and sanitize whitespace."""
    # 1. Remove XML/HTML tags (e.g. <EOS>, <pad>, <html>, etc.)
    cleaned = re.sub(r'<[^>]+>', '', raw_text)
    # 2. Retain only letters, numbers, spaces, and standard punctuation
    cleaned = re.sub(r'[^a-zA-Z0-9\s.,!?:;\'"()\-\/]', ' ', cleaned)
    # 3. Collapse horizontal whitespace
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    # 4. Strip whitespace line by line
    lines = [line.strip() for line in cleaned.splitlines()]
    cleaned = "\n".join(lines)
    # 5. Collapse excessive empty lines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()

def _download_and_extract_pdf(paper_id: str, pdf_url: str) -> tuple[str, str]:
    """Download PDF locally to arxiv_cache directory if not cached, and extract clean text."""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        local_filename = f"{paper_id.replace('/', '_')}.pdf"
        local_file_path = os.path.abspath(os.path.join(CACHE_DIR, local_filename))

        if not os.path.exists(local_file_path):
            url = pdf_url.replace("http://", "https://", 1) if pdf_url.startswith("http://") else pdf_url
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response:
                pdf_bytes = response.read()
            with open(local_file_path, "wb") as f:
                f.write(pdf_bytes)

        doc = fitz.open(local_file_path)
        pages_text = []
        for i, page in enumerate(doc):
            cleaned_page = _clean_text(page.get_text())
            if cleaned_page:
                pages_text.append(f"--- Page {i + 1} ---\n{cleaned_page}")
        
        full_text = "\n\n".join(pages_text)
        local_pdf_link = f"file://{local_file_path}"
        return local_pdf_link, full_text
    except Exception as e:
        return "", f"Error downloading or extracting paper text: {str(e)}"

@mcp.tool()
def search_arxiv_papers(query: str, max_results: int = 5) -> str:
    """
    Search arXiv for academic papers matching a query.
    Returns titles, IDs, authors, and short summaries.
    """
    search = arxiv.Search(query=query, max_results=max_results)
    results = []
    
    for paper in client.results(search):
        # Extract the pure ID from the full entry URL (e.g., '1706.03762v7' -> '1706.03762')
        paper_id = paper.entry_id.split("/abs/")[-1].split("v")[0]
        
        results.append(
            f"Title: {paper.title}\n"
            f"ID: {paper_id}\n"
            f"Authors: {', '.join([a.name for a in paper.authors])}\n"
            f"Published: {paper.published.strftime('%Y-%m-%d')}\n"
            f"PDF Link: {paper.pdf_url}\n"
            f"Summary: {paper.summary}\n"
            f"{'-'*40}"
        )
        
    return "\n".join(results) if results else "No papers found matching that query."

@mcp.tool()
def get_arxiv_paper_by_id(paper_id: str) -> str:
    """
    Retrieve full metadata, abstract, and full paper text for a specific arXiv paper using its unique ID (e.g., '1706.03762').
    Downloads the PDF to local storage and provides a local PDF link.
    """
    # Clean the ID string just in case the LLM includes formatting
    clean_id = paper_id.strip()
    search = arxiv.Search(id_list=[clean_id])
    
    try:
        paper = next(client.results(search))
        local_pdf_link, full_text = _download_and_extract_pdf(clean_id, paper.pdf_url)
        return (
            f"Title: {paper.title}\n"
            f"ID: {clean_id}\n"
            f"Authors: {', '.join([a.name for a in paper.authors])}\n"
            f"Published: {paper.published.strftime('%Y-%m-%d')}\n"
            f"Primary Category: {paper.primary_category}\n"
            f"PDF Link: {paper.pdf_url}\n"
            f"Local PDF Link: {local_pdf_link}\n\n"
            f"Full Abstract:\n{paper.summary}\n\n"
            f"Full Paper Text:\n{full_text}"
        )
    except StopIteration:
        return f"Error: No arXiv paper found with ID '{clean_id}'."

if __name__ == "__main__":
    mcp.run(transport="stdio")

