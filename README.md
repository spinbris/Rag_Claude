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

## 🌐 Web Interface (Gradio)

Launch the interactive web interface to query your documents:

```bash
./start_gradio.sh
```

The app will automatically find an available port (7860-7869) and display the URL.

**Management:**
- **Start (auto-open browser):** `./start_gradio.sh`
- **Start (manual URL):** `./start_gradio.sh no-browser`
- **Stop:** `./stop_gradio.sh` or press `Ctrl+C`

**If browser shows blank page:**
1. Stop the server (Ctrl+C)
2. Run: `./start_gradio.sh no-browser`
3. Copy the displayed URL
4. Paste it manually into your browser

### Features

**4 Interactive Tabs:**

1. **💬 Query Documents** - Ask questions in natural language
   - Adjustable retrieval parameters (top_k, max_tokens)
   - Source citations with similarity scores
   - Save results to files

2. **🔍 Semantic Search** - Find relevant chunks without LLM
   - Fast keyword/concept search
   - View exact document excerpts
   - Similarity scoring

3. **📁 Data Management** - Load and manage documents
   - Upload from `data/` directory
   - View loading statistics
   - Track skipped files and errors

4. **❓ Help** - Complete documentation
   - Usage instructions
   - Parameter explanations
   - Troubleshooting guide

**See [GRADIO_GUIDE.md](GRADIO_GUIDE.md) for detailed documentation.**

## Notes

- `RAGSystem.load_file` accepts a directory path and will recurse into subdirectories
- Unsupported file types are skipped
- All outputs are saved to `outputs/` folder
