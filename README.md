RAGSystem
==========

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository provides a Retrieval-Augmented Generation (RAG) system with **ChromaDB** vector storage.

## Features

- 🗄️ **ChromaDB Vector Storage**: Persistent, open-source vector database (no pickle files!)
- 📄 **Multi-format Support**: PDF, DOCX, CSV, TXT, Markdown, and web pages
- 🔍 **Semantic Search**: Cosine similarity-based retrieval
- 💾 **Automatic Persistence**: Data is automatically saved and loaded
- 🚀 **Knowledge Graph Ready**: Built on ChromaDB for future graph integration

## Quick Start

### 0. Installation

```bash
# Install dependencies and setup package
uv sync
uv pip install -e .
```

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

**Files Location:** All Gradio files are in the [`gradio/`](gradio/) folder.

**Management:**
- **Start (auto-open browser):** `./start_gradio.sh`
- **Start (manual URL):** `./start_gradio.sh no-browser`
- **Stop:** Click the "🛑 Exit & Shutdown Server" button in the interface
- **Alternative stop:** `./stop_gradio.sh` or press `Ctrl+C`

**The exit button automatically closes both the browser and terminal - no Ctrl+C needed!**

**If browser shows blank page:**
1. Stop the server (Ctrl+C)
2. Run: `./start_gradio.sh no-browser`
3. Copy the displayed URL
4. Paste it manually into your browser

**See [gradio/README.md](gradio/README.md) for Gradio folder details.**

### Features

**5 Interactive Tabs:**

1. **💬 Query Documents** - Ask questions in natural language
   - Adjustable retrieval parameters (top_k, max_tokens)
   - Source citations with similarity scores
   - Save results to files

2. **🔍 Semantic Search** - Find relevant chunks without LLM
   - Fast keyword/concept search
   - View exact document excerpts
   - Similarity scoring

3. **📁 Data Management** - Load and manage documents
   - **Collection Management** - Organize data into separate collections
   - Upload from `data/` directory
   - View loading statistics
   - Track skipped files and errors

4. **🌐 Web Scraping** - Load content from websites
   - Single URL loading for individual pages
   - Sitemap-based loading for entire sites
   - Automatic content extraction
   - Built-in rate limiting

5. **❓ Help** - Complete documentation
   - Usage instructions
   - Parameter explanations
   - Troubleshooting guide

**See [guides/GRADIO_GUIDE.md](guides/GRADIO_GUIDE.md) for detailed documentation.**

## 📚 Documentation

### Quick Links
- **[Quick Start Guide](guides/QUICKSTART.md)** - Get up and running in 3 steps
- **[Gradio Interface Guide](guides/GRADIO_GUIDE.md)** - Complete web UI documentation
- **[Web Scraping Guide](guides/WEB_SCRAPING_GUIDE.md)** - Scrape entire websites (sitemap & recursive)
- **[Examples](examples/README.md)** - Code examples and tutorials

### Guides Folder
All comprehensive guides are in the [`guides/`](guides/) folder:
- [QUICKSTART.md](guides/QUICKSTART.md) - Quick start guide
- [GRADIO_GUIDE.md](guides/GRADIO_GUIDE.md) - Web interface guide
- [WEB_SCRAPING_GUIDE.md](guides/WEB_SCRAPING_GUIDE.md) - Web scraping (sitemap & recursive)
- [EXIT_BUTTON_INFO.md](guides/EXIT_BUTTON_INFO.md) - Exit button documentation
- [SHUTDOWN_CLEANUP.md](guides/SHUTDOWN_CLEANUP.md) - Shutdown technical details
- [TEST_EXIT_BUTTON.md](guides/TEST_EXIT_BUTTON.md) - Exit button testing

## Notes

- `RAGSystem.load_file` accepts a directory path and will recurse into subdirectories
- Unsupported file types are skipped
- All outputs are saved to `outputs/` folder

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
