"""Gradio Web Interface for RAG System with Knowledge Graph Support.

Enhanced version with knowledge graph exploration, entity search, and graph-aware queries.

Usage:
    uv run python gradio/gradio_app_with_kg.py

Then open http://localhost:7860 in your browser.

License:
    MIT License - Copyright (c) 2025 Stephen Parton
    See LICENSE file for details.
"""

import os
import gradio as gr
from ragsystem import RAGSystem
from ragsystem import GraphRAGSystem
from ragsystem.knowledge_graph import GraphVisualizer
from datetime import datetime
import requests
import xml.etree.ElementTree as ET
from typing import List
import json

# Initialize systems
persist_directory = "outputs/chroma_db"
graph_persist_directory = "outputs/chroma_graph_db"
rag = None
graph_rag = None
current_collection = "rag_documents"
use_graph_mode = False  # Toggle between regular RAG and Graph RAG


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


def initialize_rag(collection_name="rag_documents", enable_graph=False):
    """Initialize or reinitialize the RAG system."""
    global rag, graph_rag, current_collection, use_graph_mode

    try:
        use_graph_mode = enable_graph

        if enable_graph:
            graph_rag = GraphRAGSystem(
                persist_directory=graph_persist_directory,
                collection_name=collection_name,
                enable_graph_extraction=True
            )
            current_collection = collection_name
            return f"✓ Connected to Graph RAG collection: {collection_name}"
        else:
            rag = RAGSystem(
                persist_directory=persist_directory,
                collection_name=collection_name
            )
            current_collection = collection_name
            return f"✓ Connected to collection: {collection_name}"
    except Exception as e:
        return f"❌ Error initializing RAG: {str(e)}"


def switch_mode(enable_graph):
    """Switch between regular RAG and Graph RAG."""
    result = initialize_rag(current_collection, enable_graph)
    stats = get_stats()
    return f"{result}\n\n{stats}"


def switch_collection(collection_name: str):
    """Switch to a different collection."""
    if not collection_name or not collection_name.strip():
        return "❌ Please enter a collection name."

    collection_name = collection_name.strip()
    result = initialize_rag(collection_name, use_graph_mode)
    stats = get_stats()
    return f"{result}\n\n{stats}"


def get_stats():
    """Get current database statistics."""
    active_system = graph_rag if use_graph_mode else rag

    if active_system is None:
        return "❌ RAG system not initialized"

    try:
        stats = active_system.get_stats()

        info = f"""
📊 **Database Statistics**

**Mode:** {'🕸️ Graph RAG' if use_graph_mode else '📚 Regular RAG'}
**Current Collection:** `{current_collection}`
**Total Documents:** {stats['total_documents']} chunks

**Configuration:**
- Chunk Size: {stats['chunk_size']}
- Chunk Overlap: {stats['chunk_overlap']}
- Embedding Model: {stats['embedding_model']}
- Embedding Dimensions: {stats.get('embedding_dimension', 'N/A')}
- LLM Model: {stats['llm_model']}
"""

        if use_graph_mode and graph_rag:
            info += f"""
**Knowledge Graph:**
- Total Entities: {stats.get('total_entities', 0)}
- Total Relations: {stats.get('total_relations', 0)}
- Graph Extraction: {'✓ Enabled' if stats.get('graph_enabled') else '✗ Disabled'}
"""
            if stats.get('top_entities'):
                info += "\n**Top Entities:**\n"
                for entity, count in stats['top_entities'][:5]:
                    info += f"  • {entity}: {count}\n"

        info += f"\n**Storage Location:** {graph_persist_directory if use_graph_mode else persist_directory}"

        return info
    except Exception as e:
        return f"❌ Error getting stats: {str(e)}"


def query_documents(question, top_k=5, max_tokens=500, use_graph_context=False, save_output=False):
    """Query the RAG system with optional graph context."""
    active_system = graph_rag if use_graph_mode else rag

    if active_system is None:
        return "❌ RAG system not initialized. Please click 'Initialize System' first.", ""

    if not question or not question.strip():
        return "⚠️ Please enter a question.", ""

    try:
        # Get statistics
        stats = active_system.get_stats()

        if stats['total_documents'] == 0:
            return "❌ No documents in database. Please load documents first.", ""

        # Query the system
        if use_graph_mode and use_graph_context:
            answer = graph_rag.query(
                question,
                top_k=int(top_k),
                max_tokens=int(max_tokens),
                use_graph_context=True
            )
        else:
            answer = active_system.query(question, top_k=int(top_k), max_tokens=int(max_tokens))

        # Get source documents
        search_results = active_system.search(question, top_k=int(top_k))

        # Format sources
        sources_text = "\n\n**📚 Sources Used:**\n\n"
        for i, result in enumerate(search_results, 1):
            sources_text += f"**{i}. {result['source']}** (Score: {result['score']:.3f})\n"
            sources_text += f"   _{result['content'][:200]}..._\n"

            # Add graph info if available
            if use_graph_mode and 'graph' in result:
                entities = result['graph'].get('entities', [])
                if entities:
                    sources_text += f"   *Entities: {', '.join(entities[:3])}*\n"
            sources_text += "\n"

        # Save to file if requested
        output_file = ""
        if save_output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"outputs/query_{timestamp}.txt"
            os.makedirs('outputs', exist_ok=True)

            with open(output_file, 'w') as f:
                f.write("="*80 + "\n")
                f.write(f"{'GRAPH ' if use_graph_mode else ''}RAG QUERY RESULT\n")
                f.write("="*80 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Question: {question}\n")
                f.write(f"Top-K: {top_k}\n")
                f.write(f"Graph Context: {use_graph_context}\n")
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
    active_system = graph_rag if use_graph_mode else rag

    if active_system is None:
        return "❌ RAG system not initialized."

    if not query or not query.strip():
        return "⚠️ Please enter a search query."

    try:
        results = active_system.search(query, top_k=int(top_k))

        if not results:
            return "No results found."

        output = f"**🔍 Search Results for:** _{query}_\n\n"
        output += f"**Found {len(results)} results:**\n\n"

        for i, result in enumerate(results, 1):
            output += f"### {i}. {result['source']}\n"
            output += f"**Similarity Score:** {result['score']:.3f}\n"

            # Add graph info if available
            if use_graph_mode and 'graph' in result:
                entities = result['graph'].get('entities', [])
                relations = result['graph'].get('relations', [])
                if entities:
                    output += f"**Entities:** {', '.join(entities)}\n"
                if relations:
                    output += f"**Relations:** {len(relations)} found\n"

            output += f"**Content:**\n{result['content']}\n\n"
            output += "---\n\n"

        return output

    except Exception as e:
        return f"❌ Error during search: {str(e)}"


def load_sample_data():
    """Load sample data from data/ directory."""
    active_system = graph_rag if use_graph_mode else rag

    if active_system is None:
        return "❌ RAG system not initialized."

    try:
        if not os.path.exists('data/'):
            return "❌ No data/ directory found. Please create it and add some documents."

        chunks_added = active_system.load_file('data/', verbose=False)

        file_count = sum(1 for root, _, files in os.walk('data/')
                        for f in files if not f.startswith('.'))

        result = f"""
✅ **Loading Complete!**

**Files Processed:** {file_count}
**Chunks Added:** {chunks_added}
**Mode:** {'🕸️ Graph RAG (with entity extraction)' if use_graph_mode else '📚 Regular RAG'}
**Database Location:** `{graph_persist_directory if use_graph_mode else persist_directory}`

*Note: Files already in the database may be skipped to avoid duplicates.*
"""
        return result

    except Exception as e:
        return f"❌ Error loading data: {str(e)}"


def load_single_url(url: str) -> str:
    """Load a single web page."""
    active_system = graph_rag if use_graph_mode else rag

    if active_system is None:
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
        chunks_added = active_system._process_documents(docs)

        return f"""
✅ **Page Loaded Successfully!**

**URL:** {url}

**Chunks Added:** {chunks_added}

**Mode:** {'🕸️ Graph RAG (with entity extraction)' if use_graph_mode else '📚 Regular RAG'}

**Database:** `{graph_persist_directory if use_graph_mode else persist_directory}`
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
    active_system = graph_rag if use_graph_mode else rag

    if active_system is None:
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
                chunks = active_system._process_documents(docs)
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

**Mode:** {'🕸️ Graph RAG (with entity extraction)' if use_graph_mode else '📚 Regular RAG'}

**Database:** `{graph_persist_directory if use_graph_mode else persist_directory}`
"""
        return result

    except Exception as e:
        return f"❌ Error loading sitemap: {str(e)}"


# Knowledge Graph specific functions

def get_all_entities():
    """Get all entities in the knowledge graph."""
    if not use_graph_mode or graph_rag is None:
        return "❌ Graph mode not enabled. Please enable Graph RAG mode first."

    try:
        entities = graph_rag.get_entities()

        if not entities:
            return "No entities found. Please load documents first."

        output = f"**🏷️ All Entities ({len(entities)} total):**\n\n"

        # Sort by frequency
        sorted_entities = sorted(entities.items(), key=lambda x: x[1], reverse=True)

        for entity, count in sorted_entities[:50]:  # Show top 50
            bar = "█" * min(count, 30)
            output += f"`{entity}` {bar} ({count})\n"

        if len(entities) > 50:
            output += f"\n*... and {len(entities) - 50} more entities*"

        return output

    except Exception as e:
        return f"❌ Error getting entities: {str(e)}"


def search_by_entity(entity_name, top_k=10):
    """Find all chunks mentioning a specific entity."""
    if not use_graph_mode or graph_rag is None:
        return "❌ Graph mode not enabled."

    if not entity_name or not entity_name.strip():
        return "⚠️ Please enter an entity name."

    try:
        results = graph_rag.search_by_entity(entity_name, top_k=int(top_k))

        if not results:
            return f"No chunks found mentioning entity: {entity_name}"

        output = f"**🎯 Chunks mentioning:** `{entity_name}`\n\n"
        output += f"**Found {len(results)} chunks:**\n\n"

        for i, result in enumerate(results, 1):
            output += f"### {i}. {result['source']}\n"
            output += f"**Content:**\n{result['content'][:300]}...\n\n"

            if 'graph' in result:
                entities = result['graph'].get('entities', [])
                relations = result['graph'].get('relations', [])
                if entities:
                    output += f"**Other Entities:** {', '.join([e for e in entities if e != entity_name][:5])}\n"
                if relations:
                    # Find relations involving this entity
                    relevant_rels = [r for r in relations if entity_name.lower() in r.lower()]
                    if relevant_rels:
                        output += f"**Relations:** {', '.join(relevant_rels[:3])}\n"

            output += "\n---\n\n"

        return output

    except Exception as e:
        return f"❌ Error searching by entity: {str(e)}"


def traverse_graph(start_entity, max_hops=2):
    """Traverse the knowledge graph from a starting entity."""
    if not use_graph_mode or graph_rag is None:
        return "❌ Graph mode not enabled."

    if not start_entity or not start_entity.strip():
        return "⚠️ Please enter a starting entity."

    try:
        subgraph = graph_rag.traverse_from_entity(start_entity, max_hops=int(max_hops))

        if not subgraph['entities']:
            return f"No connections found for entity: {start_entity}"

        output = f"**🕸️ Graph Traversal from:** `{start_entity}`\n\n"
        output += f"**Max Hops:** {max_hops}\n"
        output += f"**Connected Entities:** {len(subgraph['entities'])}\n\n"

        output += "**Entities Found:**\n"
        for entity in subgraph['entities'][:20]:
            output += f"  • {entity}\n"

        if len(subgraph['entities']) > 20:
            output += f"  ... and {len(subgraph['entities']) - 20} more\n"

        if subgraph['relations']:
            output += f"\n**Relationships ({len(subgraph['relations'])} total):**\n\n"
            for s, r, t in subgraph['relations'][:15]:
                output += f"  • `{s}` --[{r}]--> `{t}`\n"

            if len(subgraph['relations']) > 15:
                output += f"\n  *... and {len(subgraph['relations']) - 15} more relationships*\n"

        return output

    except Exception as e:
        return f"❌ Error traversing graph: {str(e)}"


def visualize_graph():
    """Generate graph visualization."""
    if not use_graph_mode or graph_rag is None:
        return "❌ Graph mode not enabled.", ""

    try:
        entities = graph_rag.get_entities()
        relations = graph_rag.get_relations()

        if not entities:
            return "No graph data available. Please load documents first.", ""

        # ASCII visualization
        ascii_viz = GraphVisualizer.to_ascii_art(entities, relations, max_entities=15)

        # Mermaid diagram
        entity_list = list(entities.keys())[:20]
        filtered_relations = [
            (s, r, t) for s, r, t in relations
            if s in entity_list and t in entity_list
        ]

        mermaid = GraphVisualizer.to_mermaid(entity_list, filtered_relations)

        # Save HTML visualization
        os.makedirs('outputs', exist_ok=True)
        GraphVisualizer.save_html_visualization(
            entity_list,
            filtered_relations,
            "outputs/graph_visualization.html"
        )

        html_message = "\n\n**📊 Interactive Visualization:**\nSaved to `outputs/graph_visualization.html` - Open in browser!"

        return ascii_viz + html_message, mermaid

    except Exception as e:
        return f"❌ Error visualizing graph: {str(e)}", ""


# Initialize on startup
startup_message = initialize_rag()

# Create Gradio interface
with gr.Blocks(title="RAG System - Knowledge Graph Interface", theme=gr.themes.Soft()) as app:

    gr.Markdown("""
    # 🤖 RAG System - Knowledge Graph Interface

    Query your documents with semantic search and explore knowledge graphs.
    """)

    # Mode selector at top
    with gr.Row():
        with gr.Column(scale=3):
            gr.Markdown("**System Mode:**")
        with gr.Column(scale=1):
            mode_toggle = gr.Checkbox(
                label="Enable Knowledge Graph Mode",
                value=False,
                info="Extract entities and relationships"
            )

    mode_status = gr.Markdown()

    mode_toggle.change(
        fn=switch_mode,
        inputs=mode_toggle,
        outputs=mode_status
    )

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

                    use_graph_checkbox = gr.Checkbox(
                        label="Use graph context (Graph RAG mode only)",
                        value=True,
                        info="Include entity relationships in context"
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
                inputs=[question_input, top_k_slider, max_tokens_slider, use_graph_checkbox, save_checkbox],
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
                    ["How are the main concepts related?"],
                    ["What entities are mentioned?"],
                    ["Summarize the key relationships."],
                ],
                inputs=question_input
            )

        # Tab 2: Semantic Search
        with gr.Tab("🔍 Semantic Search"):
            gr.Markdown("### Search for relevant document chunks")

            search_input = gr.Textbox(
                label="Search Query",
                placeholder="knowledge graph",
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

        # Tab 3: Knowledge Graph Explorer
        with gr.Tab("🕸️ Knowledge Graph"):
            gr.Markdown("""
            ### Explore the Knowledge Graph

            **Note:** This tab requires **Knowledge Graph Mode** to be enabled.
            """)

            with gr.Tabs():
                # Entity Explorer
                with gr.Tab("🏷️ Entities"):
                    gr.Markdown("**View all extracted entities**")

                    entities_btn = gr.Button("📋 List All Entities", variant="primary")
                    entities_output = gr.Markdown()

                    entities_btn.click(
                        fn=get_all_entities,
                        outputs=entities_output
                    )

                    gr.Markdown("---")
                    gr.Markdown("**Search by Entity**")

                    entity_search_input = gr.Textbox(
                        label="Entity Name",
                        placeholder="Enter entity name (e.g., 'Python', 'Machine Learning')"
                    )

                    entity_top_k = gr.Slider(
                        minimum=1,
                        maximum=20,
                        value=10,
                        step=1,
                        label="Max results"
                    )

                    entity_search_btn = gr.Button("🎯 Find Chunks with Entity")
                    entity_search_output = gr.Markdown()

                    entity_search_btn.click(
                        fn=search_by_entity,
                        inputs=[entity_search_input, entity_top_k],
                        outputs=entity_search_output
                    )

                # Graph Traversal
                with gr.Tab("🕸️ Traversal"):
                    gr.Markdown("**Explore connections between entities**")

                    traverse_entity_input = gr.Textbox(
                        label="Starting Entity",
                        placeholder="Enter entity name"
                    )

                    traverse_hops = gr.Slider(
                        minimum=1,
                        maximum=5,
                        value=2,
                        step=1,
                        label="Maximum hops",
                        info="How many relationship levels to explore"
                    )

                    traverse_btn = gr.Button("🚀 Traverse Graph", variant="primary")
                    traverse_output = gr.Markdown()

                    traverse_btn.click(
                        fn=traverse_graph,
                        inputs=[traverse_entity_input, traverse_hops],
                        outputs=traverse_output
                    )

                # Visualization
                with gr.Tab("📊 Visualization"):
                    gr.Markdown("**Generate graph visualizations**")

                    viz_btn = gr.Button("🎨 Generate Visualizations", variant="primary")

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("**ASCII Art:**")
                            ascii_output = gr.Markdown()

                        with gr.Column():
                            gr.Markdown("**Mermaid Diagram:**")
                            gr.Markdown("*Copy the code below to [mermaid.live](https://mermaid.live)*")
                            mermaid_output = gr.Textbox(
                                label="Mermaid Code",
                                lines=15,
                                max_lines=20,
                                interactive=False
                            )

                    viz_btn.click(
                        fn=visualize_graph,
                        outputs=[ascii_output, mermaid_output]
                    )

                    gr.Markdown("""
                    ---
                    **💡 Tip:** An interactive HTML visualization is also saved to `outputs/graph_visualization.html`
                    """)

        # Tab 4: Data Management
        with gr.Tab("📁 Data Management"):
            gr.Markdown("### Load and manage documents")

            with gr.Row():
                with gr.Column():
                    gr.Markdown("""
                    **Load Documents:**

                    Click the button below to load all documents from the `data/` directory.

                    Supported formats: PDF, DOCX, CSV, TXT, MD

                    *If Graph Mode is enabled, entities and relationships will be extracted.*
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

                    Location: `outputs/chroma_db/` (Regular) or `outputs/chroma_graph_db/` (Graph)

                    **To add documents:**
                    1. Choose mode (Regular or Graph RAG)
                    2. Place files in `data/` directory
                    3. Click "Load from data/ folder"
                    4. Wait for processing
                    5. Start querying!
                    """)

        # Tab 5: Web Scraping
        with gr.Tab("🌐 Web Scraping"):
            gr.Markdown("### Load content from websites")

            with gr.Tabs():
                # Single URL tab
                with gr.Tab("Single URL"):
                    gr.Markdown("""
                    **Load a single web page**

                    Enter any web page URL to extract and load its content.

                    *If Graph Mode is enabled, entities will be extracted from the page.*
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

                    *If Graph Mode is enabled, entities will be extracted from all pages.*
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

                            **See:** [Web Scraping Guide](../guides/WEB_SCRAPING_GUIDE.md)
                            """)

            gr.Markdown("""
            ---
            **⚠️ Web Scraping Notes:**
            - Respect website terms of service
            - Some sites may block automated access
            - Rate limiting is built-in (1-2 sec delay)
            - Large sites may take time to process
            - **Graph Mode:** Entities extracted from web content
            """)

        # Tab 6: Help
        with gr.Tab("❓ Help"):
            gr.Markdown("""
            ## How to Use This Interface

            ### 🕸️ Knowledge Graph Mode

            **What is it?**
            Knowledge Graph Mode extracts entities (people, places, concepts) and their relationships from your documents, enabling:
            - Entity-based search
            - Relationship exploration
            - Graph-aware queries (enhanced context)
            - Visual graph exploration

            **How to enable:**
            1. Check "Enable Knowledge Graph Mode" at the top
            2. Load your documents (entities will be extracted automatically)
            3. Explore the **Knowledge Graph** tab

            ### 1️⃣ Query Documents Tab

            - **Ask Questions:** Natural language questions about your documents
            - **Graph Context:** When enabled in Graph Mode, includes entity relationships in the answer
            - **Adjust Parameters:**
              - `top_k`: Number of document chunks to retrieve
              - `max_tokens`: Maximum response length
            - **Save Results:** Save query results to `outputs/` folder

            ### 2️⃣ Semantic Search Tab

            - Find relevant document chunks using semantic similarity
            - In Graph Mode, results show extracted entities
            - Useful for exploring document contents

            ### 3️⃣ Knowledge Graph Tab (Graph Mode Only)

            **Entities Subtab:**
            - View all extracted entities with frequency counts
            - Search for chunks containing specific entities

            **Traversal Subtab:**
            - Start from an entity and explore connected entities
            - Specify number of "hops" (relationship levels) to explore
            - See all relationships in the subgraph

            **Visualization Subtab:**
            - Generate ASCII art visualization
            - Generate Mermaid diagram (copy to mermaid.live)
            - Create interactive HTML visualization (opens in browser)

            ### 4️⃣ Data Management Tab

            - Load documents from `data/` directory
            - In Graph Mode, entities and relationships are extracted automatically
            - Supported formats: PDF, DOCX, CSV, TXT, Markdown

            ### 5️⃣ Web Scraping Tab

            - **Single URL:** Load content from individual web pages
            - **Sitemap:** Load multiple pages from a website's sitemap
            - **Best For:** Documentation sites, blogs, knowledge bases
            - **Graph Mode:** Entities extracted from web content
            - **Note:** Respects rate limits and removes navigation/scripts

            ### 🔄 Regular vs Graph RAG Mode

            **Regular RAG:**
            - ✅ Faster processing
            - ✅ Standard semantic search
            - ❌ No entity extraction
            - ❌ No relationship tracking

            **Graph RAG:**
            - ✅ Entity extraction
            - ✅ Relationship detection
            - ✅ Graph traversal
            - ✅ Enhanced query context
            - ⚠️ Slower processing (LLM extracts entities)

            ### 💡 Tips

            - Start with Regular RAG for quick testing
            - Use Graph RAG for in-depth knowledge exploration
            - Entity names are case-sensitive
            - Graph visualization works best with 10-30 entities
            - Interactive HTML visualizations are saved to `outputs/`

            ### 🔧 Troubleshooting

            - **"Graph mode not enabled"**: Toggle the Knowledge Graph Mode switch at the top
            - **"No entities found"**: Load documents with Graph Mode enabled
            - **Slow loading in Graph Mode**: LLM extraction takes time (use pattern-based for speed)

            ### 📁 File Locations

            - **Regular RAG Database:** `outputs/chroma_db/`
            - **Graph RAG Database:** `outputs/chroma_graph_db/`
            - **Query Results:** `outputs/query_*.txt`
            - **Graph Visualizations:** `outputs/graph_visualization.html`
            - **Input Documents:** `data/`

            ---

            ### 📄 License

            **MIT License** - © 2025 Stephen Parton

            ✅ Free to use, modify, and distribute
            ✅ Can be used in commercial projects
            📋 See LICENSE file for full details
            """)

    gr.Markdown("""
    ---
    **RAG System with Knowledge Graphs** | Built with Gradio | Powered by OpenAI | [MIT License](https://opensource.org/licenses/MIT) © 2025
    """)

# Launch the app
if __name__ == "__main__":
    print("="*80)
    print("Starting Knowledge Graph RAG System Gradio Interface")
    print("="*80)
    print(f"\n{startup_message}")
    print(f"\nPersist Directory: {persist_directory}")
    print(f"Graph Persist Directory: {graph_persist_directory}")

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
        print("❌ Could not find an available port.")
        import sys
        sys.exit(1)

    print(f"📡 Starting server on port {port}")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"\n⏳ Opening browser...\n")

    try:
        app.launch(
            server_name="127.0.0.1",
            server_port=port,
            share=False,
            show_error=True,
            inbrowser=True,
            prevent_thread_lock=False,
            quiet=False
        )
    except Exception as e:
        print(f"\n❌ Error launching Gradio: {e}")
        raise
