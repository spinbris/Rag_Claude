"""Example: Load multiple files from data folder into ChromaDB.

Run this from the project root:
    uv run python examples/load_multiple_files.py
"""

import os
import sys
from datetime import datetime

# Add parent directory to path so we can import ragsystem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragsystem import RAGSystem

# Create outputs directory if it doesn't exist
os.makedirs('outputs', exist_ok=True)

# Initialize RAG system with ChromaDB storage
print("Initializing RAG system with ChromaDB...")
rag = RAGSystem(persist_directory="outputs/chroma_db")

# Load all files from data directory
print("\n" + "="*80)
print("LOADING MULTIPLE FILES FROM DATA FOLDER")
print("="*80 + "\n")

# Load all files with verbose output to see what's being processed
summary = rag.load_file('data/', verbose=True)

# Display results
print("\n" + "="*80)
print("LOADING SUMMARY")
print("="*80)
print(f"\n✓ Total chunks added: {summary['added_chunks']}")

if summary.get('skipped_files'):
    print(f"\n⚠ Skipped files ({len(summary['skipped_files'])}):")
    for file in summary['skipped_files']:
        print(f"  - {file}")

if summary.get('errors'):
    print(f"\n❌ Errors ({len(summary['errors'])}):")
    for error in summary['errors']:
        print(f"  - {error['file']}: {error['error']}")

# Get system stats
stats = rag.get_stats()
print(f"\n📊 Database Stats:")
print(f"  Total documents: {stats['total_documents']}")
print(f"  Chunk size: {stats['chunk_size']}")
print(f"  Chunk overlap: {stats['chunk_overlap']}")
print(f"  Embedding model: {stats['embedding_model']}")
print(f"  LLM model: {stats['llm_model']}")

# Test queries on the loaded data
print("\n" + "="*80)
print("TESTING QUERIES")
print("="*80 + "\n")

queries = [
    "What documents are in this collection?",
    "Provide a brief overview of the main topics covered.",
    "What are the key recommendations or findings?"
]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"outputs/multi_file_analysis_{timestamp}.txt"

with open(output_file, 'w') as f:
    f.write("="*80 + "\n")
    f.write("MULTI-FILE RAG ANALYSIS\n")
    f.write("="*80 + "\n\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Source directory: data/\n")
    f.write(f"Total chunks: {summary['added_chunks']}\n")
    f.write(f"Total documents: {stats['total_documents']}\n\n")

    for i, question in enumerate(queries, 1):
        print(f"Query {i}: {question}")
        answer = rag.query(question, top_k=5, max_tokens=300)
        print(f"Answer: {answer}\n")

        f.write(f"\n--- QUERY {i} ---\n")
        f.write(f"Q: {question}\n")
        f.write(f"A: {answer}\n")

    f.write("\n" + "="*80 + "\n")

print(f"✓ Analysis saved to: {output_file}")

# Save a manifest of loaded files
manifest_file = f"outputs/loaded_files_{timestamp}.txt"
with open(manifest_file, 'w') as f:
    f.write("LOADED FILES MANIFEST\n")
    f.write("="*80 + "\n\n")
    f.write(f"ChromaDB Location: outputs/chroma_db\n")
    f.write(f"Total Chunks: {summary['added_chunks']}\n\n")

    # List all files in data directory
    f.write("Files processed from data/:\n")
    for root, dirs, files in os.walk('data/'):
        for file in files:
            filepath = os.path.join(root, file)
            file_size = os.path.getsize(filepath)
            f.write(f"  ✓ {filepath} ({file_size:,} bytes)\n")

    if summary.get('skipped_files'):
        f.write(f"\nSkipped files:\n")
        for file in summary['skipped_files']:
            f.write(f"  ⚠ {file}\n")

    if summary.get('errors'):
        f.write(f"\nErrors:\n")
        for error in summary['errors']:
            f.write(f"  ❌ {error['file']}: {error['error']}\n")

print(f"✓ Manifest saved to: {manifest_file}")

print("\n" + "="*80)
print("✅ COMPLETE - All files loaded into ChromaDB")
print("="*80)
print(f"\nYou can now query this data in future sessions by initializing:")
print(f'  rag = RAGSystem(persist_directory="outputs/chroma_db")')
