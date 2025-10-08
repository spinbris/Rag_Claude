RAGSystem
==========

This repository provides a Retrieval-Augmented Generation (RAG) system with **ChromaDB** vector storage.

## Features

- 🗄️ **ChromaDB Vector Storage**: Persistent, open-source vector database (no pickle files!)
- 📄 **Multi-format Support**: PDF, DOCX, CSV, TXT, Markdown, and web pages
- 🔍 **Semantic Search**: Cosine similarity-based retrieval
- 💾 **Automatic Persistence**: Data is automatically saved and loaded
- 🚀 **Knowledge Graph Ready**: Built on ChromaDB for future graph integration

## Quick Start

### 1. Load and Query Documents

```python
from ragsystem import RAGSystem

# Initialize with ChromaDB persistence
rag = RAGSystem(persist_directory="./chroma_db")

# Load documents from data/ directory
summary = rag.load_file('data/', verbose=True)
print(f"Added {summary['added_chunks']} chunks from data/")

# Query the system
answer = rag.query("What is this document about?")
print(answer)
```

### 2. Persistence (Automatic!)

ChromaDB automatically persists data. Simply initialize with the same directory:

```python
# Later, in a new session...
rag = RAGSystem(persist_directory="./chroma_db")
# Your data is already loaded!
answer = rag.query("What are the key points?")
```

## Storage

- **Vector Database**: ChromaDB (SQLite-backed)
- **Default Location**: `./chroma_db/`
- **Data Format**: Open-source, portable, secure
- No manual save/load required!

## Notes

- `RAGSystem.load_file` accepts a directory path and will recurse into subdirectories
- Unsupported file types are skipped
- All outputs are saved to `outputs/` folder
