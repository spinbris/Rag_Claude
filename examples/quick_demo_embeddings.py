#!/usr/bin/env python3
"""Quick demo of custom embeddings - minimal example."""

from ragsystem import RAGSystem
from embeddings import SentenceTransformerEmbeddings, VoyageEmbeddings

def demo_local():
    """Demo using free local embeddings."""
    print("🚀 Local Embeddings Demo (Free!)")
    print("-" * 50)

    # Create local embeddings - completely free, no API key needed
    local_emb = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2",
        device="cpu"
    )

    # Create RAG system with local embeddings
    rag = RAGSystem(
        embeddings=local_emb,
        persist_directory="./demo_local_db",
        collection_name="demo_local"
    )

    # Add some sample documents
    sample_docs = [
        {"content": "Python is a high-level programming language known for its simplicity.", "source": "python.txt", "type": "text"},
        {"content": "Machine learning is a subset of AI focused on learning from data.", "source": "ml.txt", "type": "text"},
        {"content": "RAG systems combine retrieval and generation for better AI responses.", "source": "rag.txt", "type": "text"}
    ]

    # Process documents
    from ragsystem.chunkers import TextChunker
    chunker = TextChunker(chunk_size=200, chunk_overlap=50)

    chunks = []
    for doc in sample_docs:
        text_chunks = chunker.chunk(doc['content'])
        for chunk in text_chunks:
            chunks.append({
                'content': chunk,
                'source': doc['source'],
                'type': doc['type']
            })

    # Generate embeddings and store
    texts = [chunk['content'] for chunk in chunks]
    embeddings = local_emb.embed_batch(texts)
    rag.vector_store.add_documents(chunks, embeddings)

    print(f"✅ Added {len(chunks)} chunks using local embeddings")

    # Query the system
    results = rag.search("What is Python?", top_k=2)
    print("\n📊 Search Results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. [{result['source']}] {result['content'][:80]}...")
        distance = result.get('distance', 'N/A')
        if isinstance(distance, (int, float)):
            print(f"   Similarity: {distance:.4f}")
        else:
            print(f"   Similarity: {distance}")

    # Get stats
    stats = rag.get_stats()
    print(f"\n📈 System Stats:")
    print(f"   Model: {stats['embedding_model']}")
    print(f"   Dimensions: {stats['embedding_dimension']}")
    print(f"   Documents: {stats['total_documents']}")


def demo_voyage():
    """Demo using Voyage AI embeddings."""
    print("\n\n🚀 Voyage AI Embeddings Demo")
    print("-" * 50)

    try:
        # Create Voyage embeddings
        voyage_emb = VoyageEmbeddings(model="voyage-3")

        # Create RAG system
        rag = RAGSystem(
            embeddings=voyage_emb,
            persist_directory="./demo_voyage_db",
            collection_name="demo_voyage"
        )

        print(f"✅ Initialized with Voyage AI ({voyage_emb.model})")
        print(f"   Dimensions: {voyage_emb.dimension}")

    except ValueError as e:
        print(f"⚠️  Voyage AI not configured: {e}")
        print("   Set VOYAGE_API_KEY in .env to use Voyage embeddings")
    except ImportError as e:
        print(f"⚠️  Voyage AI not installed: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("Custom Embeddings Quick Demo")
    print("=" * 50)

    demo_local()
    demo_voyage()

    print("\n" + "=" * 50)
    print("✨ Demo complete!")
    print("\nNext steps:")
    print("- See examples/custom_embeddings.py for more examples")
    print("- Read CUSTOM_EMBEDDINGS.md for full documentation")
