"""Test ChromaDB persistence - query without reloading PDF."""

from ragsystem import RAGSystem

# Initialize RAG system - should load existing ChromaDB data
print("Initializing RAG system with existing ChromaDB...")
rag = RAGSystem(persist_directory="outputs/chroma_db")

# Check if data exists
stats = rag.get_stats()
print(f"Documents in database: {stats['total_documents']}")

if stats['total_documents'] == 0:
    print("No documents found! You need to run test_summary.py first.")
else:
    # Query without loading any new data
    print("\nQuerying existing data...")
    summary = rag.query(
        "What are the key governance recommendations in this document?",
        top_k=5,
        max_tokens=200
    )

    print("\n--- ANSWER ---")
    print(summary)
    print("\n✓ Successfully queried persisted ChromaDB data!")
