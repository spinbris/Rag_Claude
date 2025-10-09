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
import requests
import xml.etree.ElementTree as ET
from typing import List

# Initialize RAG system
persist_directory = "outputs/chroma_db"
rag = None
current_collection = "rag_documents"


def get_available_collections():
    """Get list of available collections in the database."""
    try:
        from ragsystem.storage.chroma_storage import ChromaVectorStore
        import chromadb
        from chromadb.config import Settings

        client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False, allow_reset=False)
        )
        collections = client.list_collections()
        return [coll.name for coll in collections]
    except Exception as e:
        print(f"Error getting collections: {e}")
        return []


def initialize_rag(collection_name="rag_documents"):
    """Initialize or reinitialize the RAG system."""
    global rag, current_collection
    try:
        rag = RAGSystem(
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        current_collection = collection_name
        return f"✓ Connected to collection: {collection_name}"
    except Exception as e:
        return f"❌ Error initializing RAG: {str(e)}"


def switch_collection(collection_name: str):
    """Switch to a different collection."""
    if not collection_name or not collection_name.strip():
        return "❌ Please enter a collection name."

    collection_name = collection_name.strip()
    result = initialize_rag(collection_name)
    stats = get_stats()
    return f"{result}\n\n{stats}"


def get_stats():
    """Get current database statistics."""
    if rag is None:
        return "❌ RAG system not initialized"

    try:
        stats = rag.get_stats()
        collections = rag.vector_store.get_collections()

        info = f"""
📊 **Database Statistics**

**Current Collection:** `{current_collection}`
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


def load_single_url(url: str) -> str:
    """Load a single web page."""
    if rag is None:
        return "❌ RAG system not initialized."

    if not url or not url.strip():
        return "❌ Please enter a URL."

    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        from loaders import WebLoader
        loader = WebLoader(timeout=15)

        print(f"Loading: {url}")
        docs = loader.load(url)

        # Process and add to RAG
        chunks_added = rag._process_documents(docs)

        return f"""
✅ **Page Loaded Successfully!**

**URL:** {url}

**Chunks Added:** {chunks_added}

**Database:** `outputs/chroma_db/`
"""
    except Exception as e:
        return f"❌ Error loading URL: {str(e)}"


def get_sitemap_urls(sitemap_url: str, max_urls: int = 50) -> List[str]:
    """Extract URLs from sitemap.xml"""
    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        urls = []
        for loc in root.findall('.//ns:loc', namespace):
            if loc.text:
                urls.append(loc.text)
                if len(urls) >= max_urls:
                    break

        # Try without namespace if none found
        if not urls:
            for loc in root.findall('.//loc'):
                if loc.text:
                    urls.append(loc.text)
                    if len(urls) >= max_urls:
                        break

        return urls[:max_urls]
    except Exception as e:
        raise ValueError(f"Error parsing sitemap: {str(e)}")


def load_from_sitemap(sitemap_url: str, max_pages: int = 20) -> str:
    """Load multiple pages from a sitemap."""
    if rag is None:
        return "❌ RAG system not initialized."

    if not sitemap_url or not sitemap_url.strip():
        return "❌ Please enter a sitemap URL."

    sitemap_url = sitemap_url.strip()
    if not sitemap_url.startswith(('http://', 'https://')):
        sitemap_url = 'https://' + sitemap_url

    try:
        # Get URLs from sitemap
        urls = get_sitemap_urls(sitemap_url, max_urls=max_pages)

        if not urls:
            return f"❌ No URLs found in sitemap: {sitemap_url}"

        from loaders import WebLoader
        loader = WebLoader(timeout=15)

        total_chunks = 0
        successful = 0
        failed = []

        for i, url in enumerate(urls, 1):
            try:
                print(f"Loading {i}/{len(urls)}: {url}")
                docs = loader.load(url)
                chunks = rag._process_documents(docs)
                total_chunks += chunks
                successful += 1
            except Exception as e:
                failed.append(f"{url}: {str(e)[:50]}")
                print(f"  ✗ Failed: {e}")

        result = f"""
✅ **Sitemap Loading Complete!**

**Sitemap URL:** {sitemap_url}

**Pages Found:** {len(urls)}

**Successfully Loaded:** {successful}

**Failed:** {len(failed)}
{chr(10).join(f'  • {f}' for f in failed[:3])}

**Total Chunks Added:** {total_chunks}

**Database:** `outputs/chroma_db/`
"""
        return result

    except Exception as e:
        return f"❌ Error loading sitemap: {str(e)}"


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

            # Collection Management Section
            with gr.Accordion("🗂️ Collection Management", open=False):
                gr.Markdown("""
                **Manage ChromaDB Collections**

                Collections let you organize different types of data separately:
                - **documents** - PDF files and text documents
                - **web_content** - Scraped web pages
                - **knowledge_base** - Curated knowledge articles
                - Or create your own custom collections!
                """)

                with gr.Row():
                    with gr.Column():
                        collection_input = gr.Textbox(
                            label="Collection Name",
                            placeholder="Enter collection name (e.g., 'web_content')",
                            value=current_collection
                        )
                        switch_btn = gr.Button("🔄 Switch Collection", variant="secondary")
                        collection_output = gr.Markdown()

                        switch_btn.click(
                            fn=switch_collection,
                            inputs=collection_input,
                            outputs=collection_output
                        )

                    with gr.Column():
                        gr.Markdown("""
                        **Tips:**
                        - Switching creates the collection if it doesn't exist
                        - All subsequent loads go to the active collection
                        - Query/search only searches the active collection
                        - Collections persist across sessions

                        **Example Collections:**
                        - `rag_documents` (default)
                        - `web_content`
                        - `product_docs`
                        - `company_knowledge`
                        """)

            gr.Markdown("---")

            # Document Loading Section
            with gr.Row():
                with gr.Column():
                    gr.Markdown("""
                    **Load Documents:**

                    Click the button below to load all documents from the `data/` directory.

                    Supported formats: PDF, DOCX, CSV, TXT, MD

                    *Documents will be added to the current collection.*
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
                    1. (Optional) Switch to desired collection
                    2. Place files in `data/` directory
                    3. Click "Load from data/ folder"
                    4. Wait for processing
                    5. Start querying!
                    """)

        # Tab 4: Web Scraping
        with gr.Tab("🌐 Web Scraping"):
            gr.Markdown("### Load content from websites")

            with gr.Tabs():
                # Single URL tab
                with gr.Tab("Single URL"):
                    gr.Markdown("""
                    **Load a single web page**

                    Enter any web page URL to extract and load its content.
                    """)

                    with gr.Row():
                        with gr.Column():
                            url_input = gr.Textbox(
                                label="Web Page URL",
                                placeholder="https://example.com/page",
                                lines=1
                            )
                            url_btn = gr.Button("🔗 Load Page", variant="primary")
                            url_output = gr.Markdown()

                            url_btn.click(
                                fn=load_single_url,
                                inputs=url_input,
                                outputs=url_output
                            )

                        with gr.Column():
                            gr.Markdown("""
                            **Tips:**
                            - Enter full URL (e.g., https://example.com)
                            - Works with most public web pages
                            - Extracts main text content
                            - Removes scripts, styles, navigation

                            **Examples:**
                            - Blog posts
                            - Documentation pages
                            - News articles
                            - Product pages
                            """)

                # Sitemap tab
                with gr.Tab("Sitemap (Multiple Pages)"):
                    gr.Markdown("""
                    **Load multiple pages from a sitemap**

                    Enter a sitemap.xml URL to load multiple pages at once.
                    This is the recommended way to scrape entire websites.
                    """)

                    with gr.Row():
                        with gr.Column():
                            sitemap_url_input = gr.Textbox(
                                label="Sitemap URL",
                                placeholder="https://example.com/sitemap.xml",
                                lines=1
                            )
                            sitemap_max_pages = gr.Slider(
                                minimum=1,
                                maximum=100,
                                value=20,
                                step=1,
                                label="Maximum pages to load"
                            )
                            sitemap_btn = gr.Button("📑 Load from Sitemap", variant="primary")
                            sitemap_output = gr.Markdown()

                            sitemap_btn.click(
                                fn=load_from_sitemap,
                                inputs=[sitemap_url_input, sitemap_max_pages],
                                outputs=sitemap_output
                            )

                        with gr.Column():
                            gr.Markdown("""
                            **How to find sitemaps:**
                            - Try: `https://example.com/sitemap.xml`
                            - Try: `https://example.com/sitemap_index.xml`
                            - Check: `https://example.com/robots.txt`
                            - Search: "site:example.com sitemap"

                            **Best Practices:**
                            - Start with 10-20 pages to test
                            - Increase limit for larger sites
                            - Loading may take several minutes
                            - Failed pages are skipped automatically

                            **See:** [Web Scraping Guide](../guides/WEB_SCRAPING_GUIDE.md) for more details
                            """)

            gr.Markdown("""
            ---
            **⚠️ Web Scraping Notes:**
            - Respect website terms of service
            - Some sites may block automated access
            - Rate limiting is built-in (1-2 sec delay)
            - Large sites may take time to process
            """)

        # Tab 5: Help
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

            - **Collection Management:** Organize data into separate collections
              - Switch between collections (e.g., `documents`, `web_content`)
              - All collections use the same database
              - Query only searches the active collection
            - **Load Documents:** Import files from the `data/` directory
            - **Supported Formats:** PDF, DOCX, CSV, TXT, Markdown
            - **Note:** Documents are added to the current collection

            ### 4️⃣ Web Scraping Tab

            - **Single URL:** Load content from individual web pages
            - **Sitemap:** Load multiple pages from a website's sitemap
            - **Best For:** Documentation sites, blogs, knowledge bases
            - **Note:** Respects rate limits and removes navigation/scripts

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
