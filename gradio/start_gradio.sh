#!/bin/bash

# Start the Gradio RAG Interface
# Usage: ./start_gradio.sh [no-browser]
# Can be run from project root or from gradio/ folder

# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root so Python can find modules
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Starting RAG System Gradio App"
echo "=========================================="
echo ""

# Check if user wants to disable auto browser opening
if [ "$1" == "no-browser" ] || [ "$1" == "--no-browser" ]; then
    echo "🚀 Starting in manual browser mode"
    echo "   (browser will NOT open automatically)"
    echo ""
    echo "⌨️  Press Ctrl+C to stop the server"
    echo ""
    uv run python gradio/gradio_app_no_browser.py
else
    echo "🚀 Starting with auto browser opening"
    echo "   (browser should open automatically)"
    echo ""
    echo "💡 Tip: If browser doesn't work, try:"
    echo "   ./start_gradio.sh no-browser"
    echo ""
    echo "⌨️  Press Ctrl+C to stop the server"
    echo ""
    uv run python gradio/gradio_app.py
fi
