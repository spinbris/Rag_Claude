"""Gradio Web Interface for RAG System with ChromaDB.

A simple, interactive web interface for querying documents stored in ChromaDB.

Usage:
    uv run python gradio_app.py

Then open http://localhost:7860 in your browser.

License:
    MIT License - Copyright (c) 2025 Stephen Parton
    See LICENSE file for details.
"""

import os
import gradio as gr
from ragsystem import RAGSystem
from datetime import datetime

# Initialize RAG system
persist_directory = "outputs/chroma_db"
rag = None


def initialize_rag(collection_name="rag_documents"):
    """Initialize or reinitialize the RAG system."""
    global rag
    try:
        rag = RAGSystem(
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        return f"✓ Connected to collection: {collection_name}"
    except Exception as e:
        return f"❌ Error initializing RAG: {str(e)}"


def get_stats():
    """Get current database statistics."""
    if rag is None:
        return "❌ RAG system not initialized"

    try:
        stats = rag.get_stats()
        collections = rag.vector_store.get_collections()

        info = f"""
📊 **Database Statistics**

**Current Collection:** rag_documents
**Total Documents:** {stats['total_documents']} chunks

**Configuration:**
- Chunk Size: {stats['chunk_size']}
- Chunk Overlap: {stats['chunk_overlap']}
- Embedding Model: {stats['embedding_model']}
- LLM Model: {stats['llm_model']}

**Available Collections:** {len(collections)}
{chr(10).join(f'  • {col}' for col in collections)}

**Storage Location:** {persist_directory}
"""
        return info
    except Exception as e:
        return f"❌ Error getting stats: {str(e)}"


def query_documents(question, top_k=5, max_tokens=500, save_output=False):
    """Query the RAG system."""
    if rag is None:
        return "❌ RAG system not initialized. Please click 'Initialize System' first.", ""

    if not question or not question.strip():
        return "⚠️ Please enter a question.", ""

    try:
        # Get statistics
        stats = rag.get_stats()

        if stats['total_documents'] == 0:
            return "❌ No documents in database. Please load documents first using the examples.", ""

        # Query the system
        answer = rag.query(question, top_k=int(top_k), max_tokens=int(max_tokens))

        # Get source documents
        search_results = rag.search(question, top_k=int(top_k))

        # Format sources
        sources_text = "\n\n**📚 Sources Used:**\n\n"
        for i, result in enumerate(search_results, 1):
            sources_text += f"**{i}. {result['source']}** (Score: {result['score']:.3f})\n"
            sources_text += f"   _{result['content'][:200]}..._\n\n"

        # Save to file if requested
        output_file = ""
        if save_output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"outputs/query_{timestamp}.txt"
            os.makedirs('outputs', exist_ok=True)

            with open(output_file, 'w') as f:
                f.write("="*80 + "\n")
                f.write("RAG QUERY RESULT\n")
                f.write("="*80 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Question: {question}\n")
                f.write(f"Top-K: {top_k}\n")
                f.write(f"Max Tokens: {max_tokens}\n\n")
                f.write("ANSWER:\n")
                f.write(answer + "\n\n")
                f.write("SOURCES:\n")
                for i, result in enumerate(search_results, 1):
                    f.write(f"{i}. {result['source']} (Score: {result['score']:.3f})\n")
                    f.write(f"   {result['content']}\n\n")
                f.write("="*80 + "\n")

            output_file = f"\n\n💾 Saved to: {output_file}"

        return answer + output_file, sources_text

    except Exception as e:
        return f"❌ Error during query: {str(e)}", ""


def search_only(query, top_k=10):
    """Search documents without LLM generation."""
    if rag is None:
        return "❌ RAG system not initialized."

    if not query or not query.strip():
        return "⚠️ Please enter a search query."

    try:
        results = rag.search(query, top_k=int(top_k))

        if not results:
            return "No results found."

        output = f"**🔍 Search Results for:** _{query}_\n\n"
        output += f"**Found {len(results)} results:**\n\n"

        for i, result in enumerate(results, 1):
            output += f"### {i}. {result['source']}\n"
            output += f"**Similarity Score:** {result['score']:.3f}\n"
            output += f"**Content:**\n{result['content']}\n\n"
            output += "---\n\n"

        return output

    except Exception as e:
        return f"❌ Error during search: {str(e)}"


def load_sample_data():
    """Load sample data from data/ directory."""
    if rag is None:
        return "❌ RAG system not initialized."

    try:
        if not os.path.exists('data/'):
            return "❌ No data/ directory found. Please create it and add some documents."

        # Use verbose=False to actually load files into ChromaDB
        # verbose=True only counts chunks without loading them
        chunks_added = rag.load_file('data/', verbose=False)

        # Count files in data directory
        file_count = sum(1 for root, _, files in os.walk('data/')
                        for f in files if not f.startswith('.'))

        result = f"""
✅ **Loading Complete!**

**Files Processed:** {file_count}

**Chunks Added:** {chunks_added}

**Database Location:** `outputs/chroma_db/`

*Note: Files already in the database may be skipped to avoid duplicates.*
"""
        return result

    except Exception as e:
        return f"❌ Error loading data: {str(e)}"


def shutdown_server():
    """Shutdown the Gradio server gracefully."""
    import sys
    import threading
    import os
    import signal
    import warnings

    def stop():
        print("\n" + "="*80)
        print("🛑 SHUTDOWN REQUESTED")
        print("="*80)
        print("\n✓ Closing server...")
        print("✓ Terminal will close automatically in 2 seconds...")
        print("\n" + "="*80 + "\n")

        # Give time for the message to display
        import time
        time.sleep(2)

        # Suppress resource tracker warnings during shutdown
        warnings.filterwarnings("ignore", category=UserWarning, message=".*resource_tracker.*")

        # Use os._exit for immediate termination without cleanup
        # This prevents resource tracker warnings about leaked semaphores
        os._exit(0)

    # Start shutdown in background thread
    threading.Thread(target=stop, daemon=True).start()

    return "✅ **Server shutting down...**\n\n**The terminal will close automatically.**\n\nYou can close this browser tab now."


# Initialize RAG on startup
startup_message = initialize_rag()

# Create Gradio interface
with gr.Blocks(title="RAG System - ChromaDB Query Interface", theme=gr.themes.Soft()) as app:

    gr.Markdown("""
    # 🤖 RAG System - ChromaDB Query Interface

    Query your documents stored in ChromaDB using natural language.
    """)

    with gr.Tabs():
        # Tab 1: Query Interface
        with gr.Tab("💬 Query Documents"):
            gr.Markdown("### Ask questions about your documents")

            with gr.Row():
                with gr.Column(scale=2):
                    question_input = gr.Textbox(
                        label="Your Question",
                        placeholder="What is this document about?",
                        lines=3
                    )

                    with gr.Row():
                        top_k_slider = gr.Slider(
                            minimum=1,
                            maximum=20,
                            value=5,
                            step=1,
                            label="Number of chunks to retrieve (top_k)"
                        )
                        max_tokens_slider = gr.Slider(
                            minimum=100,
                            maximum=1000,
                            value=500,
                            step=50,
                            label="Max response length (tokens)"
                        )

                    save_checkbox = gr.Checkbox(
                        label="Save result to file",
                        value=False
                    )

                    query_btn = gr.Button("🔍 Ask Question", variant="primary", size="lg")

                with gr.Column(scale=1):
                    stats_display = gr.Markdown(get_stats())
                    refresh_stats_btn = gr.Button("🔄 Refresh Stats")

            answer_output = gr.Markdown(label="Answer")
            sources_output = gr.Markdown(label="Sources")

            query_btn.click(
                fn=query_documents,
                inputs=[question_input, top_k_slider, max_tokens_slider, save_checkbox],
                outputs=[answer_output, sources_output]
            )

            refresh_stats_btn.click(
                fn=get_stats,
                outputs=stats_display
            )

            # Example questions
            gr.Markdown("### 💡 Example Questions")
            gr.Examples(
                examples=[
                    ["What is the main topic of these documents?"],
                    ["What are the key recommendations?"],
                    ["Summarize the governance requirements."],
                    ["What are the climate-related risks mentioned?"],
                    ["Who published these documents?"],
                ],
                inputs=question_input
            )

        # Tab 2: Semantic Search
        with gr.Tab("🔍 Semantic Search"):
            gr.Markdown("### Search for relevant document chunks (no LLM generation)")

            search_input = gr.Textbox(
                label="Search Query",
                placeholder="climate change risks",
                lines=2
            )

            search_top_k = gr.Slider(
                minimum=1,
                maximum=20,
                value=10,
                step=1,
                label="Number of results"
            )

            search_btn = gr.Button("🔍 Search", variant="primary")
            search_output = gr.Markdown(label="Search Results")

            search_btn.click(
                fn=search_only,
                inputs=[search_input, search_top_k],
                outputs=search_output
            )

        # Tab 3: Data Management
        with gr.Tab("📁 Data Management"):
            gr.Markdown("### Load and manage documents")

            with gr.Row():
                with gr.Column():
                    gr.Markdown("""
                    **Load Documents:**

                    Click the button below to load all documents from the `data/` directory.

                    Supported formats: PDF, DOCX, CSV, TXT, MD
                    """)

                    load_btn = gr.Button("📂 Load from data/ folder", variant="primary")
                    load_output = gr.Markdown()

                    load_btn.click(
                        fn=load_sample_data,
                        outputs=load_output
                    )

                with gr.Column():
                    gr.Markdown("""
                    **Current Database:**

                    Location: `outputs/chroma_db/`

                    **To add documents:**
                    1. Place files in `data/` directory
                    2. Click "Load from data/ folder"
                    3. Wait for processing
                    4. Start querying!
                    """)

        # Tab 4: Help
        with gr.Tab("❓ Help"):
            gr.Markdown("""
            ## How to Use This Interface

            ### 1️⃣ Query Documents Tab

            - **Ask Questions:** Enter natural language questions about your documents
            - **Adjust Parameters:**
              - `top_k`: Number of document chunks to retrieve (more = more context)
              - `max_tokens`: Maximum length of the response
            - **Save Results:** Check the box to save query results to `outputs/` folder

            ### 2️⃣ Semantic Search Tab

            - **Search without LLM:** Find relevant document chunks using semantic similarity
            - **Use Cases:**
              - Find specific topics or keywords
              - Explore document contents
              - Check what's in your database

            ### 3️⃣ Data Management Tab

            - **Load Documents:** Import files from the `data/` directory
            - **Supported Formats:** PDF, DOCX, CSV, TXT, Markdown
            - **Note:** Documents are automatically stored in ChromaDB

            ### 📊 Understanding the Stats

            - **Total Documents:** Number of text chunks in the database
            - **Chunk Size:** Max characters per chunk
            - **Chunk Overlap:** Overlapping characters between chunks
            - **Collections:** Separate namespaces in the database

            ### 💡 Tips

            - More specific questions get better answers
            - Increase `top_k` for complex questions requiring more context
            - Use semantic search to explore what's in your database
            - All query results can be saved to files for later reference

            ### 🔧 Troubleshooting

            - **"No documents in database"**: Load documents using the Data Management tab
            - **"RAG system not initialized"**: Refresh the page
            - **Slow responses**: Large `top_k` or `max_tokens` take longer to process

            ### 📁 File Locations

            - **ChromaDB:** `outputs/chroma_db/`
            - **Query Results:** `outputs/query_*.txt`
            - **Input Documents:** `data/`

            ### 🚀 Advanced Usage

            For programmatic access, see the examples in `examples/` folder:
            - `load_multiple_files.py` - Batch loading
            - `manage_collections.py` - Collection management
            - `add_to_existing_collection.py` - Incremental loading

            ---

            ### 📄 License

            This project is licensed under the **MIT License**.

            **What this means:**
            - ✅ Free to use, modify, and distribute
            - ✅ Can be used in commercial projects
            - ✅ No warranty or liability
            - 📋 See the LICENSE file for full details

            **Copyright © 2025 Stephen Parton**
            """)

    gr.Markdown("""
    ---
    **RAG System with ChromaDB** | Built with Gradio | Powered by OpenAI | [MIT License](https://opensource.org/licenses/MIT) © 2025
    """)

    # Exit/Shutdown Section
    with gr.Row():
        with gr.Column(scale=4):
            gr.Markdown("")  # Spacer
        with gr.Column(scale=1):
            shutdown_output = gr.Markdown("")
            shutdown_btn = gr.Button("🛑 Exit & Shutdown Server", variant="stop", size="sm")
            shutdown_btn.click(
                fn=shutdown_server,
                outputs=shutdown_output
            )

# Launch the app
if __name__ == "__main__":
    print("="*80)
    print("Starting RAG System Gradio Interface")
    print("="*80)
    print(f"\n{startup_message}")
    print(f"\nPersist Directory: {persist_directory}")

    if rag:
        stats = rag.get_stats()
        print(f"Documents in database: {stats['total_documents']}")
        print(f"Embedding model: {stats['embedding_model']}")
        print(f"LLM model: {stats['llm_model']}")

    print("\n" + "="*80)
    print("🚀 Launching Gradio interface...")
    print("="*80 + "\n")

    # Try to find an available port
    import socket

    def find_free_port(start_port=7860, max_attempts=10):
        """Find an available port starting from start_port."""
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("0.0.0.0", port))
                    return port
            except OSError:
                continue
        return None

    port = find_free_port()
    if port is None:
        print("❌ Could not find an available port. Please close other applications using ports 7860-7869.")
        import sys
        sys.exit(1)

    print(f"📡 Starting server on port {port}")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"\n⏳ Waiting for server to start...")
    print(f"   The browser will open automatically when ready.\n")
    print(f"   If the browser doesn't open, manually visit: http://localhost:{port}\n")

    try:
        app.launch(
            server_name="127.0.0.1",  # Use localhost instead of 0.0.0.0
            server_port=port,
            share=False,
            show_error=True,
            inbrowser=True,  # Automatically open browser
            prevent_thread_lock=False,  # Ensure server stays running
            quiet=False  # Show startup messages
        )
    except Exception as e:
        print(f"\n❌ Error launching Gradio: {e}")
        print(f"\nTry manually opening: http://localhost:{port}")
        raise
