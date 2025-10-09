"""Example of using custom embedding providers with RAGSystem.

This example demonstrates how to use:
1. Local embeddings (Sentence Transformers) - free, privacy-focused
2. Voyage AI embeddings - high-quality API-based embeddings
3. OpenAI embeddings (default)
"""

from ragsystem import RAGSystem
from embeddings import SentenceTransformerEmbeddings, VoyageEmbeddings, OpenAIEmbeddings


def example_local_embeddings():
    """Use local Sentence Transformer embeddings (free, runs on your machine)."""
    print("\n" + "="*60)
    print("Example 1: Local Embeddings (Sentence Transformers)")
    print("="*60)

    # Create local embeddings instance
    # Popular models:
    # - all-MiniLM-L6-v2: Fast, lightweight (384 dimensions)
    # - all-mpnet-base-v2: Better quality (768 dimensions)
    local_embeddings = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2",
        device="cpu"  # or "cuda" for GPU
    )

    # Initialize RAG with local embeddings
    rag = RAGSystem(
        embeddings=local_embeddings,
        persist_directory="./chroma_db_local",
        collection_name="local_embeddings_demo"
    )

    # Load some documents
    print("\nLoading documents with local embeddings...")
    rag.load_file("data/", verbose=True)

    # Query the system
    print("\nQuerying with local embeddings...")
    answer = rag.query("What is this document about?")
    print(f"\nAnswer: {answer}")

    # Get stats
    stats = rag.get_stats()
    print(f"\nStats:")
    print(f"  Embedding Model: {stats['embedding_model']}")
    print(f"  Embedding Dimension: {stats['embedding_dimension']}")
    print(f"  Total Documents: {stats['total_documents']}")


def example_voyage_embeddings():
    """Use Voyage AI embeddings (API-based, high quality)."""
    print("\n" + "="*60)
    print("Example 2: Voyage AI Embeddings")
    print("="*60)

    # Create Voyage embeddings instance
    # Models:
    # - voyage-3: Latest general-purpose (1024 dimensions)
    # - voyage-3-lite: Faster, cost-effective (512 dimensions)
    # - voyage-code-3: Optimized for code (1024 dimensions)
    voyage_embeddings = VoyageEmbeddings(
        model="voyage-3"  # API key from VOYAGE_API_KEY env var
    )

    # Initialize RAG with Voyage embeddings
    rag = RAGSystem(
        embeddings=voyage_embeddings,
        persist_directory="./chroma_db_voyage",
        collection_name="voyage_embeddings_demo"
    )

    # Load some documents
    print("\nLoading documents with Voyage embeddings...")
    rag.load_file("data/", verbose=True)

    # Query the system
    print("\nQuerying with Voyage embeddings...")
    answer = rag.query("What is this document about?")
    print(f"\nAnswer: {answer}")

    # Get stats
    stats = rag.get_stats()
    print(f"\nStats:")
    print(f"  Embedding Model: {stats['embedding_model']}")
    print(f"  Embedding Dimension: {stats['embedding_dimension']}")
    print(f"  Total Documents: {stats['total_documents']}")


def example_openai_embeddings():
    """Use OpenAI embeddings (default behavior)."""
    print("\n" + "="*60)
    print("Example 3: OpenAI Embeddings (Default)")
    print("="*60)

    # Option 1: Use default (implicitly creates OpenAI embeddings)
    rag = RAGSystem(
        embedding_model="text-embedding-3-small",
        persist_directory="./chroma_db_openai",
        collection_name="openai_embeddings_demo"
    )

    # Option 2: Explicitly create OpenAI embeddings
    # openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    # rag = RAGSystem(embeddings=openai_embeddings, ...)

    print("\nLoading documents with OpenAI embeddings...")
    rag.load_file("data/", verbose=True)

    print("\nQuerying with OpenAI embeddings...")
    answer = rag.query("What is this document about?")
    print(f"\nAnswer: {answer}")

    stats = rag.get_stats()
    print(f"\nStats:")
    print(f"  Embedding Model: {stats['embedding_model']}")
    print(f"  Embedding Dimension: {stats['embedding_dimension']}")
    print(f"  Total Documents: {stats['total_documents']}")


def compare_embeddings():
    """Compare different embedding providers on the same query."""
    print("\n" + "="*60)
    print("Example 4: Comparing Embedding Providers")
    print("="*60)

    query = "What are the main topics discussed?"

    # Test with local embeddings
    print("\n--- Local Embeddings ---")
    local_rag = RAGSystem(
        embeddings=SentenceTransformerEmbeddings("all-MiniLM-L6-v2"),
        persist_directory="./chroma_db_local",
        collection_name="compare_local"
    )
    local_results = local_rag.search(query, top_k=3)
    print(f"Top result: {local_results[0]['content'][:100]}...")

    # Test with Voyage embeddings
    print("\n--- Voyage Embeddings ---")
    voyage_rag = RAGSystem(
        embeddings=VoyageEmbeddings("voyage-3"),
        persist_directory="./chroma_db_voyage",
        collection_name="compare_voyage"
    )
    voyage_results = voyage_rag.search(query, top_k=3)
    print(f"Top result: {voyage_results[0]['content'][:100]}...")

    # Test with OpenAI embeddings
    print("\n--- OpenAI Embeddings ---")
    openai_rag = RAGSystem(
        embedding_model="text-embedding-3-small",
        persist_directory="./chroma_db_openai",
        collection_name="compare_openai"
    )
    openai_results = openai_rag.search(query, top_k=3)
    print(f"Top result: {openai_results[0]['content'][:100]}...")


if __name__ == "__main__":
    print("Custom Embeddings Examples for RAGSystem")
    print("=========================================")

    # Run examples
    # example_local_embeddings()    # Free, runs locally
    # example_voyage_embeddings()   # Requires VOYAGE_API_KEY
    # example_openai_embeddings()   # Requires OPENAI_API_KEY (default)
    # compare_embeddings()          # Compare all providers

    print("\n\nUncomment the example you want to run in the main section!")
    print("\nTips:")
    print("- Local embeddings: Free, privacy-focused, no API key needed")
    print("- Voyage embeddings: High quality, optimized for retrieval")
    print("- OpenAI embeddings: Good general purpose, easy to use")
