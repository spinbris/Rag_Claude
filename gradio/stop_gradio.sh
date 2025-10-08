#!/bin/bash

# Stop any running Gradio instances
# Usage: ./stop_gradio.sh

echo "🔍 Checking for running Gradio processes..."

# Find processes using ports 7860-7869
for port in {7860..7869}; do
    pid=$(lsof -ti :$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "Found process $pid on port $port"
        echo "Stopping process $pid..."
        kill $pid
        sleep 1

        # Force kill if still running
        if ps -p $pid > /dev/null 2>&1; then
            echo "Force stopping process $pid..."
            kill -9 $pid
        fi
        echo "✓ Stopped process on port $port"
    fi
done

# Also check for any python processes running gradio_app.py
gradio_pids=$(pgrep -f "gradio_app.py")
if [ ! -z "$gradio_pids" ]; then
    echo "Found Gradio app processes: $gradio_pids"
    for pid in $gradio_pids; do
        echo "Stopping process $pid..."
        kill $pid
    done
fi

echo ""
echo "✅ All Gradio processes stopped"
echo ""
echo "You can now run: ./start_gradio.sh"
