#!/bin/zsh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

export PYTHONPATH="$PROJECT_ROOT"
cd "$PROJECT_ROOT"

echo "=== Running Unit Tests ==="
uv run pytest unittests/
