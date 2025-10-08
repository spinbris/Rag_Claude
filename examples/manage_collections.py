"""Example: Managing ChromaDB collections.

This shows how to:
- Create multiple collections for different purposes
- Clear collections
- Switch between collections
- List all collections

Run this from the project root:
    uv run python examples/manage_collections.py
"""

import os
import sys
from datetime import datetime

# Add parent directory to path so we can import ragsystem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragsystem import RAGSystem

os.makedirs('outputs', exist_ok=True)

print("="*80)
print("CHROMADB COLLECTION MANAGEMENT")
print("="*80 + "\n")

# Example 1: Create separate collections for different document types
print("Example 1: Multiple Collections for Organization")
print("-"*80 + "\n")

# Collection 1: Financial documents
print("Creating 'finance_docs' collection...")
rag_finance = RAGSystem(
    persist_directory="outputs/chroma_db",
    collection_name="finance_docs"
)
print(f"  Documents in finance_docs: {len(rag_finance.vector_store)}")

# Collection 2: Research papers
print("\nCreating 'research_papers' collection...")
rag_research = RAGSystem(
    persist_directory="outputs/chroma_db",
    collection_name="research_papers"
)
print(f"  Documents in research_papers: {len(rag_research.vector_store)}")

# Collection 3: Default collection
print("\nCreating default 'rag_documents' collection...")
rag_default = RAGSystem(
    persist_directory="outputs/chroma_db",
    collection_name="rag_documents"
)
print(f"  Documents in rag_documents: {len(rag_default.vector_store)}")

# List all collections
print("\n" + "="*80)
print("All Collections in Database:")
print("="*80)
collections = rag_default.vector_store.get_collections()
for i, col in enumerate(collections, 1):
    print(f"{i}. {col}")

# Example 2: Load different data into different collections
print("\n" + "="*80)
print("Example 2: Loading Data into Specific Collections")
print("="*80 + "\n")

# Load data into default collection
print("Loading data/ into default collection...")
summary = rag_default.load_file('data/', verbose=True)
print(f"✓ Loaded {summary['added_chunks']} chunks into 'rag_documents'")

stats_default = rag_default.get_stats()
print(f"  Total documents: {stats_default['total_documents']}")

# Example 3: Query specific collections
print("\n" + "="*80)
print("Example 3: Querying Different Collections")
print("="*80 + "\n")

if stats_default['total_documents'] > 0:
    query = "What is the main topic of these documents?"
    print(f"Query to 'rag_documents': {query}")
    answer = rag_default.query(query, top_k=3, max_tokens=200)
    print(f"Answer: {answer}\n")

# Example 4: Clear a collection
print("="*80)
print("Example 4: Clearing a Collection")
print("="*80 + "\n")

print(f"Before clear - rag_documents has {len(rag_default.vector_store)} documents")
print("Clearing 'rag_documents' collection...")
rag_default.vector_store.clear()
print(f"After clear - rag_documents has {len(rag_default.vector_store)} documents")

# Example 5: Delete a collection
print("\n" + "="*80)
print("Example 5: Deleting a Collection")
print("="*80 + "\n")

# Create a temporary collection
print("Creating temporary collection 'temp_collection'...")
rag_temp = RAGSystem(
    persist_directory="outputs/chroma_db",
    collection_name="temp_collection"
)

print("\nCollections before delete:")
collections_before = rag_default.vector_store.get_collections()
for col in collections_before:
    print(f"  - {col}")

print("\nDeleting 'temp_collection'...")
rag_temp.vector_store.delete_collection("temp_collection")

print("\nCollections after delete:")
collections_after = rag_default.vector_store.get_collections()
for col in collections_after:
    print(f"  - {col}")

# Best Practices
print("\n" + "="*80)
print("💡 BEST PRACTICES")
print("="*80 + "\n")

best_practices = """
1. **Organize by Purpose**
   - Use different collections for different document types or projects
   - Example: 'finance_reports', 'research_papers', 'customer_docs'

2. **Naming Conventions**
   - Use descriptive collection names
   - Use lowercase with underscores: 'my_collection_name'

3. **Persistence**
   - All collections in the same persist_directory share the same database
   - Collections persist automatically - no manual save needed

4. **Clearing vs Deleting**
   - clear(): Removes all documents but keeps the collection
   - delete_collection(): Removes the entire collection

5. **Multiple Databases**
   - Use different persist_directory for completely separate databases
   - Example:
     - outputs/chroma_db/         (production)
     - outputs/chroma_db_test/    (testing)
     - outputs/chroma_db_archive/ (archive)
"""

print(best_practices)

# Save summary
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"outputs/collection_management_{timestamp}.txt"

with open(output_file, 'w') as f:
    f.write("="*80 + "\n")
    f.write("CHROMADB COLLECTION MANAGEMENT SUMMARY\n")
    f.write("="*80 + "\n\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Database Location: outputs/chroma_db\n\n")
    f.write("Collections:\n")
    for col in collections_after:
        f.write(f"  - {col}\n")
    f.write("\n" + best_practices)
    f.write("\n" + "="*80 + "\n")

print(f"\n✓ Summary saved to: {output_file}")
