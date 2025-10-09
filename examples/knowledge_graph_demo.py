"""
Knowledge Graph RAG Demo - Works with ANY Embedding Provider!

This demonstrates how to use knowledge graphs with:
1. Local embeddings (Sentence Transformers)
2. Voyage AI embeddings
3. OpenAI embeddings

The key insight: Graph relationships are stored as metadata,
while embeddings (from ANY provider) are used for semantic search.
"""

from ragsystem.graph_rag import GraphRAGSystem
from embeddings import SentenceTransformerEmbeddings, VoyageEmbeddings, OpenAIEmbeddings
from ragsystem.knowledge_graph import GraphVisualizer


def demo_graph_with_local_embeddings():
    """Demo: Knowledge Graph + Local Embeddings (FREE!)"""
    print("\n" + "=" * 70)
    print("Demo 1: Knowledge Graph with Local Embeddings (FREE!)")
    print("=" * 70)

    # Create local embeddings
    local_emb = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")

    # Create Graph RAG with local embeddings
    graph_rag = GraphRAGSystem(
        embeddings=local_emb,
        persist_directory="./demo_graph_local",
        collection_name="graph_local_demo",
        enable_graph_extraction=True  # Enable graph extraction
    )

    # Add sample documents
    print("\n📚 Loading sample documents...")
    sample_data = [
        {
            "content": "Python is a high-level programming language. Python was created by Guido van Rossum. Python is widely used for machine learning and data science.",
            "source": "python_intro.txt",
            "type": "text"
        },
        {
            "content": "Machine learning is a subset of artificial intelligence. Machine learning uses statistical techniques. Deep learning is a type of machine learning that uses neural networks.",
            "source": "ml_basics.txt",
            "type": "text"
        },
        {
            "content": "RAG systems combine retrieval and generation. RAG uses vector databases for retrieval. ChromaDB is a vector database used in RAG systems.",
            "source": "rag_overview.txt",
            "type": "text"
        }
    ]

    chunks_added = graph_rag._process_documents(sample_data)
    print(f"✅ Added {chunks_added} chunks with graph extraction")

    # Get graph statistics
    stats = graph_rag.get_stats()
    print(f"\n📊 Graph Statistics:")
    print(f"   Embedding Model: {stats['embedding_model']}")
    print(f"   Embedding Dimensions: {stats['embedding_dimension']}")
    print(f"   Total Entities: {stats['total_entities']}")
    print(f"   Total Relations: {stats['total_relations']}")

    # Show top entities
    if stats['top_entities']:
        print(f"\n🔝 Top Entities:")
        for entity, count in stats['top_entities'][:5]:
            print(f"   • {entity}: {count} occurrences")

    # Semantic search (using local embeddings!)
    print(f"\n🔍 Semantic Search: 'What is Python?'")
    results = graph_rag.search("What is Python?", top_k=2)
    for i, result in enumerate(results, 1):
        print(f"\n   Result {i} (score: {result['score']:.3f}):")
        print(f"   {result['content'][:100]}...")
        if 'graph' in result:
            print(f"   Entities: {', '.join(result['graph']['entities'][:3])}")

    # Entity-based search
    print(f"\n🎯 Entity Search: 'Python'")
    entity_results = graph_rag.search_by_entity("Python", top_k=2)
    print(f"   Found {len(entity_results)} chunks mentioning 'Python'")

    # Graph traversal
    print(f"\n🕸️  Graph Traversal from 'Python':")
    subgraph = graph_rag.traverse_from_entity("Python", max_hops=2)
    print(f"   Connected entities: {', '.join(subgraph['entities'][:5])}")
    if subgraph['relations']:
        print(f"   Sample relations:")
        for s, r, t in subgraph['relations'][:3]:
            print(f"   • {s} -{r}-> {t}")

    # Query with graph context
    print(f"\n💬 Query with Graph Context:")
    answer = graph_rag.query(
        "How is Python related to machine learning?",
        top_k=3,
        use_graph_context=True
    )
    print(f"   {answer}")

    return graph_rag


def demo_graph_with_voyage_embeddings():
    """Demo: Knowledge Graph + Voyage AI Embeddings"""
    print("\n\n" + "=" * 70)
    print("Demo 2: Knowledge Graph with Voyage AI Embeddings")
    print("=" * 70)

    try:
        # Create Voyage embeddings
        voyage_emb = VoyageEmbeddings("voyage-3")

        # Create Graph RAG with Voyage embeddings
        graph_rag = GraphRAGSystem(
            embeddings=voyage_emb,
            persist_directory="./demo_graph_voyage",
            collection_name="graph_voyage_demo",
            enable_graph_extraction=True
        )

        print(f"\n✅ Initialized Graph RAG with Voyage embeddings")
        print(f"   Model: {voyage_emb.model_name}")
        print(f"   Dimensions: {voyage_emb.dimension}")

        # Same document loading and querying as before...
        print("\n   (Load documents and query similar to Demo 1)")

    except (ValueError, ImportError) as e:
        print(f"\n⚠️  Voyage AI not configured: {e}")
        print("   Set VOYAGE_API_KEY in .env to use Voyage embeddings")


def demo_visualization(graph_rag: GraphRAGSystem):
    """Demo: Visualize the knowledge graph"""
    print("\n\n" + "=" * 70)
    print("Demo 3: Knowledge Graph Visualization")
    print("=" * 70)

    # Get graph data
    entities = graph_rag.get_entities()
    relations = graph_rag.get_relations()

    if not entities:
        print("\n⚠️  No graph data available. Run demo 1 first.")
        return

    # ASCII visualization
    print("\n📊 ASCII Art Visualization:")
    ascii_viz = GraphVisualizer.to_ascii_art(entities, relations, max_entities=10)
    print(ascii_viz)

    # Mermaid diagram
    print("\n📝 Mermaid Diagram (copy to https://mermaid.live):")
    entity_list = list(entities.keys())[:10]  # Limit for readability
    filtered_relations = [
        (s, r, t) for s, r, t in relations
        if s in entity_list and t in entity_list
    ]
    mermaid = GraphVisualizer.to_mermaid(entity_list, filtered_relations)
    print(mermaid)

    # Save HTML visualization
    print("\n🌐 Saving interactive HTML visualization...")
    GraphVisualizer.save_html_visualization(
        entity_list,
        filtered_relations,
        "outputs/knowledge_graph.html"
    )
    print("   Open outputs/knowledge_graph.html in your browser!")

    # Cytoscape format (for programmatic use)
    cyto_data = GraphVisualizer.to_cytoscape(entity_list, filtered_relations)
    print(f"\n📦 Cytoscape.js data generated: {len(cyto_data['nodes'])} nodes, {len(cyto_data['edges'])} edges")


def compare_embeddings_with_graphs():
    """Compare how different embeddings work with the same knowledge graph"""
    print("\n\n" + "=" * 70)
    print("Demo 4: Compare Embeddings with Knowledge Graphs")
    print("=" * 70)

    query = "What technologies are used in machine learning?"

    print(f"\n🔍 Query: '{query}'")
    print("\n" + "-" * 70)

    # Test with local embeddings
    print("\n1️⃣  Local Embeddings (Sentence Transformers):")
    local_emb = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")
    local_rag = GraphRAGSystem(
        embeddings=local_emb,
        persist_directory="./demo_graph_local",
        collection_name="graph_local_demo"
    )
    local_results = local_rag.search(query, top_k=2)
    if local_results:
        print(f"   Top result: {local_results[0]['content'][:80]}...")
        print(f"   Score: {local_results[0]['score']:.3f}")
        if 'graph' in local_results[0]:
            print(f"   Entities: {', '.join(local_results[0]['graph']['entities'][:3])}")

    print("\n2️⃣  The graph data is the SAME regardless of embedding provider!")
    entities = local_rag.get_entities()
    relations = local_rag.get_relations()
    print(f"   Total entities: {len(entities)}")
    print(f"   Total relations: {len(relations)}")
    print("\n   Key insight: Embeddings affect retrieval quality,")
    print("   but the knowledge graph structure is consistent!")


def main():
    """Run all demonstrations"""
    print("=" * 70)
    print("Knowledge Graph RAG with Multiple Embedding Providers")
    print("=" * 70)

    # Create outputs directory
    import os
    os.makedirs("outputs", exist_ok=True)

    # Demo 1: Local embeddings + Knowledge graph
    graph_rag = demo_graph_with_local_embeddings()

    # Demo 2: Voyage embeddings + Knowledge graph
    demo_graph_with_voyage_embeddings()

    # Demo 3: Visualization
    demo_visualization(graph_rag)

    # Demo 4: Compare embeddings
    compare_embeddings_with_graphs()

    print("\n\n" + "=" * 70)
    print("✨ All demonstrations complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("1. Knowledge graphs work with ANY embedding provider")
    print("2. Graph relationships are stored as metadata in ChromaDB")
    print("3. Embeddings are used for semantic search")
    print("4. You can switch embedding providers without losing graph data")
    print("\nNext steps:")
    print("- Open outputs/knowledge_graph.html for interactive visualization")
    print("- Try with your own documents!")
    print("- Experiment with different embedding models")


if __name__ == "__main__":
    main()
