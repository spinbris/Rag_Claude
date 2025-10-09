#!/usr/bin/env python3
"""Quick Knowledge Graph Demo - Minimal example showing graphs work with any embeddings."""

import os
os.makedirs("outputs", exist_ok=True)

print("=" * 70)
print("Knowledge Graph + Custom Embeddings Demo")
print("=" * 70)

# Choose your embedding provider
print("\nChoose embedding provider:")
print("1. Local (Sentence Transformers) - FREE")
print("2. Voyage AI - Your API key is configured!")
print("3. OpenAI - Default")

choice = input("\nEnter choice (1-3) [default: 1]: ").strip() or "1"

from ragsystem import GraphRAGSystem
from ragsystem.knowledge_graph import GraphVisualizer

if choice == "1":
    print("\n🆓 Using Local Embeddings (free!)")
    from embeddings import SentenceTransformerEmbeddings
    embeddings = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")
    db_dir = "./quick_demo_local"

elif choice == "2":
    print("\n🚀 Using Voyage AI Embeddings")
    from embeddings import VoyageEmbeddings
    embeddings = VoyageEmbeddings("voyage-3")
    db_dir = "./quick_demo_voyage"

else:
    print("\n✨ Using OpenAI Embeddings (default)")
    embeddings = None  # Will use default OpenAI
    db_dir = "./quick_demo_openai"

# Create GraphRAG system
print(f"\n📦 Initializing Graph RAG...")
graph_rag = GraphRAGSystem(
    embeddings=embeddings,
    enable_graph_extraction=True,
    persist_directory=db_dir,
    collection_name="quick_demo"
)

# Sample data
sample_docs = [
    {
        "content": """
        Python is a high-level programming language created by Guido van Rossum.
        Python is widely used for machine learning and data science applications.
        Python has a simple syntax that makes it easy to learn.
        """,
        "source": "python.txt",
        "type": "text"
    },
    {
        "content": """
        Machine learning is a subset of artificial intelligence.
        Machine learning uses statistical techniques to enable computers to learn from data.
        Deep learning is a type of machine learning that uses neural networks.
        Python is the most popular language for machine learning.
        """,
        "source": "ml.txt",
        "type": "text"
    },
    {
        "content": """
        RAG systems combine retrieval and generation for better AI responses.
        RAG uses vector databases like ChromaDB for document retrieval.
        RAG systems can incorporate knowledge graphs for structured information.
        Embeddings are used in RAG for semantic similarity search.
        """,
        "source": "rag.txt",
        "type": "text"
    }
]

print(f"📚 Loading {len(sample_docs)} sample documents...")
chunks = graph_rag._process_documents(sample_docs)
print(f"✅ Loaded {chunks} chunks with graph extraction")

# Get stats
stats = graph_rag.get_stats()
print(f"\n📊 System Statistics:")
print(f"   Embedding Model: {stats['embedding_model']}")
print(f"   Embedding Dimensions: {stats['embedding_dimension']}")
print(f"   Total Entities: {stats['total_entities']}")
print(f"   Total Relations: {stats['total_relations']}")

if stats['top_entities']:
    print(f"\n🔝 Top Entities:")
    for entity, count in stats['top_entities'][:5]:
        print(f"   • {entity}: {count} occurrences")

# Semantic search
print(f"\n🔍 Semantic Search: 'What is Python?'")
results = graph_rag.search("What is Python?", top_k=2)
for i, result in enumerate(results, 1):
    print(f"\n   Result {i} (score: {result['score']:.3f}):")
    print(f"   {result['content'][:100].strip()}...")
    if 'graph' in result and result['graph']['entities']:
        print(f"   Entities: {', '.join(result['graph']['entities'][:3])}")

# Entity search
print(f"\n🎯 Entity Search: Find chunks mentioning 'Python'")
entity_results = graph_rag.search_by_entity("Python", top_k=3)
print(f"   Found {len(entity_results)} chunks")

# Graph traversal
print(f"\n🕸️  Graph Traversal: Start from 'Python', explore 2 hops")
subgraph = graph_rag.traverse_from_entity("Python", max_hops=2)
print(f"   Connected entities: {', '.join(subgraph['entities'][:6])}")

if subgraph['relations']:
    print(f"   Sample relationships:")
    for s, r, t in subgraph['relations'][:3]:
        print(f"   • {s} --[{r}]--> {t}")

# Graph-aware query
print(f"\n💬 Graph-Aware Query:")
print(f"   Question: 'How is Python related to machine learning?'")
answer = graph_rag.query(
    "How is Python related to machine learning?",
    top_k=3,
    use_graph_context=True
)
print(f"\n   Answer: {answer}")

# Visualization
print(f"\n📊 Generating Visualizations...")

entities = graph_rag.get_entities()
relations = graph_rag.get_relations()

# ASCII
print("\n" + "=" * 70)
ascii_viz = GraphVisualizer.to_ascii_art(entities, relations, max_entities=10)
print(ascii_viz)

# Interactive HTML
entity_list = list(entities.keys())[:20]
filtered_relations = [
    (s, r, t) for s, r, t in relations
    if s in entity_list and t in entity_list
]

GraphVisualizer.save_html_visualization(
    entity_list,
    filtered_relations,
    "outputs/quick_demo_graph.html"
)

print("\n" + "=" * 70)
print("✨ Demo Complete!")
print("=" * 70)

print(f"\n📁 Files created:")
print(f"   • outputs/quick_demo_graph.html - Interactive visualization")
print(f"\n🎯 Key Takeaway:")
print(f"   Knowledge graphs work with ANY embedding provider!")
print(f"   Graph structure is stored as metadata, separate from embeddings.")

print(f"\n💡 Try this:")
print(f"   • Open outputs/quick_demo_graph.html in your browser")
print(f"   • Run again with a different embedding provider")
print(f"   • Load your own documents!")
