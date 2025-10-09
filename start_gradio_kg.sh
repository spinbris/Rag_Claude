#!/bin/bash

# Start Gradio interface with Knowledge Graph support
# Usage: ./start_gradio_kg.sh [no-browser]

echo "Starting Gradio Knowledge Graph Interface..."

# Check if no-browser flag is set
NO_BROWSER=""
if [ "$1" = "no-browser" ]; then
    NO_BROWSER="no-browser"
    echo "Browser auto-open disabled"
fi

# Kill any existing Gradio processes
pkill -f "gradio_app_with_kg.py" 2>/dev/null

# Start Gradio with uv
if [ "$NO_BROWSER" = "no-browser" ]; then
    # Modify the script to disable browser opening
    TEMP_FILE=$(mktemp)
    sed 's/inbrowser=True/inbrowser=False/' gradio/gradio_app_with_kg.py > "$TEMP_FILE"
    uv run python "$TEMP_FILE"
    rm "$TEMP_FILE"
else
    uv run python gradio/gradio_app_with_kg.py
fi
