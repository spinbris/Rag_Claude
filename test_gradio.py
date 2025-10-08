"""Quick test to verify Gradio app functionality."""

import os
import sys

# Test imports
try:
    import gradio as gr
    print("✓ Gradio installed")
except ImportError:
    print("❌ Gradio not installed. Run: uv add gradio")
    sys.exit(1)

try:
    from ragsystem import RAGSystem
    print("✓ RAGSystem available")
except ImportError:
    print("❌ RAGSystem import failed")
    sys.exit(1)

# Test ChromaDB connection
try:
    rag = RAGSystem(persist_directory="outputs/chroma_db")
    stats = rag.get_stats()
    print(f"✓ ChromaDB connected ({stats['total_documents']} documents)")
except Exception as e:
    print(f"❌ ChromaDB connection failed: {e}")
    sys.exit(1)

# Test basic query function
if stats['total_documents'] > 0:
    try:
        answer = rag.query("What is this about?", top_k=3, max_tokens=100)
        print(f"✓ Query successful (response length: {len(answer)} chars)")
    except Exception as e:
        print(f"❌ Query failed: {e}")
        sys.exit(1)
else:
    print("⚠️  No documents in database - query test skipped")

print("\n" + "="*60)
print("✅ All checks passed! Gradio app should work correctly.")
print("="*60)
print("\nTo start the Gradio interface:")
print("  ./start_gradio.sh")
print("\nOr:")
print("  uv run python gradio_app.py")
print("\nThen open: http://localhost:7860")
