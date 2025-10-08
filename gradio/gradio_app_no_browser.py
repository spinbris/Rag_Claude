"""Gradio Web Interface - Manual Browser Opening Version

This version does NOT automatically open the browser.
Instead, it prints the URL for you to copy and paste into your browser.

Usage:
    uv run python gradio_app_no_browser.py

Then manually open the displayed URL in your browser.
"""

# Import the main app
import sys
import os

# Modify the original launch to not open browser
if __name__ == "__main__":
    print("="*80)
    print("Starting RAG System Gradio Interface (Manual Browser Mode)")
    print("="*80)
    print("\n⚠️  This version will NOT automatically open your browser.")
    print("    You will need to manually open the URL shown below.\n")

    # Import and modify the gradio_app module
    import gradio_app

    # Get the original app
    app = gradio_app.app

    # Find a free port
    import socket
    def find_free_port(start_port=7860, max_attempts=10):
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("127.0.0.1", port))
                    return port
            except OSError:
                continue
        return None

    port = find_free_port()
    if port is None:
        print("❌ Could not find an available port. Run ./stop_gradio.sh first.")
        sys.exit(1)

    print("="*80)
    print(f"🚀 Server starting on port {port}")
    print("="*80)
    print(f"\n📋 COPY THIS URL:")
    print(f"\n    http://localhost:{port}")
    print(f"\n📝 Paste it into your web browser (Chrome, Safari, Firefox, etc.)")
    print(f"\n⌨️  Press Ctrl+C to stop the server\n")
    print("="*80 + "\n")

    # Launch without opening browser
    app.launch(
        server_name="127.0.0.1",
        server_port=port,
        share=False,
        show_error=True,
        inbrowser=False,  # DO NOT auto-open browser
        prevent_thread_lock=False,
        quiet=False
    )
