"""Example: Add new files to an existing ChromaDB collection.

This demonstrates incremental loading - adding new documents
to an existing ChromaDB collection without reloading everything.

Run this from the project root:
    uv run python examples/add_to_existing_collection.py
"""

import os
import sys
from datetime import datetime

# Add parent directory to path so we can import ragsystem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragsystem import RAGSystem

# Create outputs directory if it doesn't exist
os.makedirs('outputs', exist_ok=True)

print("="*80)
print("INCREMENTAL LOADING - Add to Existing ChromaDB Collection")
print("="*80 + "\n")

# Initialize RAG system - connects to existing ChromaDB
print("Connecting to existing ChromaDB collection...")
rag = RAGSystem(persist_directory="outputs/chroma_db")

# Check current state
initial_stats = rag.get_stats()
print(f"\n📊 Current State:")
print(f"  Total documents: {initial_stats['total_documents']}")

# Example 1: Add a single PDF file
print("\n" + "-"*80)
print("Example 1: Adding a single PDF file")
print("-"*80)

# Check if there are any new PDFs to add
import glob
all_pdfs = glob.glob('data/*.pdf')
print(f"\nFound {len(all_pdfs)} PDF files in data/:")
for pdf in all_pdfs:
    print(f"  - {pdf}")

# Example 2: Add files from a specific subdirectory
print("\n" + "-"*80)
print("Example 2: Adding files from a subdirectory")
print("-"*80)

# You can create subdirectories in data/ for organization
# Example structure:
#   data/
#   ├── finance/
#   │   ├── report1.pdf
#   │   └── report2.pdf
#   └── research/
#       ├── paper1.pdf
#       └── paper2.md

subdirs = [d for d in glob.glob('data/*/') if os.path.isdir(d)]
if subdirs:
    print(f"\nFound {len(subdirs)} subdirectories:")
    for subdir in subdirs:
        print(f"  - {subdir}")
        # Load from specific subdirectory
        print(f"    Loading files from {subdir}...")
        summary = rag.load_file(subdir, verbose=True)
        print(f"    ✓ Added {summary['added_chunks']} chunks")
else:
    print("\nNo subdirectories found in data/")
    print("You can organize files like this:")
    print("  data/")
    print("  ├── category1/")
    print("  │   └── document1.pdf")
    print("  └── category2/")
    print("      └── document2.pdf")

# Example 3: Add a specific file type
print("\n" + "-"*80)
print("Example 3: Adding specific file types")
print("-"*80)

# Find markdown files
md_files = glob.glob('data/**/*.md', recursive=True)
if md_files:
    print(f"\nFound {len(md_files)} Markdown files:")
    for md_file in md_files:
        print(f"  - {md_file}")
        chunks = rag.load_file(md_file)
        print(f"    ✓ Added {chunks} chunks")
else:
    print("\nNo Markdown files found")

# Check final state
final_stats = rag.get_stats()
print("\n" + "="*80)
print("FINAL STATISTICS")
print("="*80)
print(f"\n📊 Before: {initial_stats['total_documents']} documents")
print(f"📊 After:  {final_stats['total_documents']} documents")
print(f"📈 Added:  {final_stats['total_documents'] - initial_stats['total_documents']} documents")

# Test query on combined data
print("\n" + "="*80)
print("TEST QUERY ON COMBINED DATA")
print("="*80 + "\n")

query = "What topics are covered across all the documents?"
print(f"Query: {query}")
answer = rag.query(query, top_k=10, max_tokens=400)
print(f"\nAnswer:\n{answer}")

# Save summary
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"outputs/incremental_load_{timestamp}.txt"

with open(output_file, 'w') as f:
    f.write("="*80 + "\n")
    f.write("INCREMENTAL LOADING SUMMARY\n")
    f.write("="*80 + "\n\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"ChromaDB Location: outputs/chroma_db\n\n")
    f.write(f"Initial documents: {initial_stats['total_documents']}\n")
    f.write(f"Final documents: {final_stats['total_documents']}\n")
    f.write(f"Documents added: {final_stats['total_documents'] - initial_stats['total_documents']}\n\n")
    f.write(f"Test Query: {query}\n")
    f.write(f"Answer: {answer}\n")
    f.write("="*80 + "\n")

print(f"\n✓ Summary saved to: {output_file}")

print("\n" + "="*80)
print("💡 TIP: ChromaDB automatically persists all changes!")
print("="*80)
print("\nNext time you initialize with the same persist_directory,")
print("all your documents will be available immediately.")
