#!/bin/zsh
export PYTHONPATH=.

echo "=== Running Integration Tests ==="
# Run arxiv tests
#uv run integration/tools/arxiv/test_mcp_arxiv_search.py
#uv run integration/tools/arxiv/test_mcp_arxiv_read_paper.py

# Run wordpress tests
#uv run integration/tools/wordpress/test_mcp_wordpress_create.py
#uv run integration/tools/wordpress/test_mcp_wordpress_edit.py
#uv run integration/tools/wordpress/test_mcp_wordpress_delete.py
#uv run integration/tools/wordpress/test_mcp_wordpress_get.py

# Web Search DuckDuckGo tests
#uv run integration/tools/websearch_duckduck/test_mcp_websearch_duckduck_search.py
uv run integration/tools/websearch_duckduck/test_mcp_websearch_duckduck_fetchpage.py
