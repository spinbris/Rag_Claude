# RAGSystem Examples

This folder contains practical examples demonstrating how to use the RAGSystem with ChromaDB.

## Prerequisites

Ensure you have:
- Installed dependencies: `uv sync`
- Set up your OpenAI API key in `.env` file
- PDF files in the `data/` folder

## Running Examples

All examples should be run from the **project root**:

```bash
uv run python examples/<example_name>.py
```

## Available Examples

### 1. 📄 Single PDF Summary
**File:** `pdf_summary.py`

Load a single PDF and generate a summary.

```bash
uv run python examples/pdf_summary.py
```

**What it does:**
- Loads PDF from `data/` folder
- Generates embeddings with OpenAI
- Stores in ChromaDB (`outputs/chroma_db/`)
- Creates a summary using GPT-4
- Saves output to timestamped file in `outputs/`

---

### 2. 📚 Load Multiple Files
**File:** `load_multiple_files.py`

Load all supported files from the data directory into ChromaDB.

```bash
uv run python examples/load_multiple_files.py
```

**What it does:**
- Recursively walks `data/` directory
- Loads all supported file types (PDF, DOCX, CSV, TXT, MD)
- Shows loading progress and statistics
- Runs test queries on combined data
- Generates analysis report and file manifest
- Saves all outputs to `outputs/` folder

**Supported formats:**
- PDF (`.pdf`)
- Word Documents (`.docx`, `.doc`)
- CSV (`.csv`)
- Text files (`.txt`)
- Markdown (`.md`, `.markdown`)

---

### 3. ➕ Incremental Loading
**File:** `add_to_existing_collection.py`

Add new documents to an existing ChromaDB collection.

```bash
uv run python examples/add_to_existing_collection.py
```

**What it does:**
- Connects to existing ChromaDB collection
- Shows current document count
- Demonstrates adding files incrementally
- Shows how to organize data in subdirectories
- Tests queries on combined dataset

**Use cases:**
- Adding new documents without reprocessing existing ones
- Organizing files by category (finance/, research/, etc.)
- Building up a knowledge base over time

---

### 4. 🌐 Web Scraping - Sitemap Method ⭐
**File:** `web_scraping_sitemap.py`

Scrape an entire website using its sitemap.xml (RECOMMENDED method).

```bash
uv run python examples/web_scraping_sitemap.py
```

**What it does:**
- Fetches sitemap.xml from a website
- Extracts all URL locations
- Loads each page into ChromaDB
- Handles sitemap indexes (sitemap of sitemaps)
- Generates scraping report

**Why use this:**
- ✅ Fast - Direct URLs, no crawling
- ✅ Complete - Gets all indexed pages
- ✅ Respectful - Uses site's official index
- ✅ Efficient - No duplicate pages

**Example sitemaps:**
- `https://docs.python.org/3/sitemap.xml`
- `https://example.com/sitemap_index.xml`

---

### 5. 🕷️ Web Scraping - Recursive Method
**File:** `web_scraping_recursive.py`

Recursively crawl a website by following links.

```bash
uv run python examples/web_scraping_recursive.py
```

**What it does:**
- Starts from a base URL
- Extracts and follows all links
- Crawls up to specified depth
- Respects rate limits (delays between requests)
- Generates crawl report

**Use cases:**
- No sitemap available
- Small sites only
- Testing/development

**⚠️  Warning:** Can be slow and may hit rate limits. Use sitemap method when possible.

**See [Web Scraping Guide](../guides/WEB_SCRAPING_GUIDE.md) for detailed comparison and best practices.**

---

### 6. 🗄️ Collection Management
**File:** `manage_collections.py`

Manage multiple ChromaDB collections.

```bash
uv run python examples/manage_collections.py
```

**What it does:**
- Create multiple collections for different purposes
- List all collections in database
- Load data into specific collections
- Clear collection contents
- Delete collections
- Best practices for organization

**Key concepts:**
- **Collections**: Separate namespaces within same database
- **Persist Directory**: Database location (can have multiple databases)
- **Clear vs Delete**: Remove documents vs remove entire collection

---

## Output Files

All examples save outputs to the `outputs/` folder:

```
outputs/
├── chroma_db/                    # ChromaDB persistent storage
│   ├── chroma.sqlite3           # Vector database (SQLite)
│   └── <uuid>/                  # Collection data
├── summary_*.txt                # Generated summaries
├── multi_file_analysis_*.txt    # Multi-file analysis
├── loaded_files_*.txt           # File manifests
└── collection_management_*.txt  # Collection info
```

## Quick Reference

### Initialize RAG System

```python
from ragsystem import RAGSystem

# Default location (./chroma_db/)
rag = RAGSystem()

# Custom location
rag = RAGSystem(persist_directory="outputs/chroma_db")

# Named collection
rag = RAGSystem(
    persist_directory="outputs/chroma_db",
    collection_name="my_documents"
)
```

### Load Documents

```python
# Single file
chunks = rag.load_pdf('data/document.pdf')

# All files in directory
summary = rag.load_file('data/', verbose=True)

# Specific file types
rag.load_markdown('data/notes.md')
rag.load_csv('data/spreadsheet.csv')
```

### Query Documents

```python
# Simple query
answer = rag.query("What is this document about?")

# With parameters
answer = rag.query(
    "What are the key findings?",
    top_k=5,           # Number of chunks to retrieve
    max_tokens=300     # Max response length
)

# Search only (no LLM)
results = rag.search("climate change", top_k=10)
for result in results:
    print(f"Score: {result['score']}")
    print(f"Content: {result['content']}")
```

### Manage Collections

```python
# Get statistics
stats = rag.get_stats()
print(f"Documents: {stats['total_documents']}")

# Clear collection (remove all documents)
rag.vector_store.clear()

# List all collections
collections = rag.vector_store.get_collections()

# Delete a collection
rag.vector_store.delete_collection("old_collection")
```

## Tips & Best Practices

### 📁 Organizing Data

Structure your `data/` folder by category:

```
data/
├── finance/
│   ├── report_2023.pdf
│   └── budget.csv
├── research/
│   ├── paper1.pdf
│   └── notes.md
└── reference/
    └── manual.pdf
```

Then load by category:
```python
rag.load_file('data/finance/')   # Load only finance docs
rag.load_file('data/research/')  # Load only research docs
```

### 🔄 Persistence

ChromaDB automatically saves all changes. No manual save needed!

```python
# Session 1: Load data
rag = RAGSystem(persist_directory="./db")
rag.load_file('data/')

# Session 2: Query (data already loaded!)
rag = RAGSystem(persist_directory="./db")
answer = rag.query("What did I load?")  # Works immediately!
```

### 🎯 Multiple Collections

Use collections to organize different document sets:

```python
# Production documents
prod = RAGSystem(persist_directory="./db", collection_name="production")
prod.load_file('data/prod/')

# Test documents
test = RAGSystem(persist_directory="./db", collection_name="testing")
test.load_file('data/test/')

# Both collections persist in same database!
```

### 🧹 Cleaning Up

```python
# Remove documents but keep collection
rag.vector_store.clear()

# Remove entire collection
rag.vector_store.delete_collection("old_collection")

# Start fresh
rag = RAGSystem(persist_directory="./new_db")
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'ragsystem'"

Run from project root:
```bash
cd /path/to/Rag_Claude
uv run python examples/example_name.py
```

### "PDFLoader is not available"

Install optional dependencies:
```bash
uv add pypdf python-docx beautifulsoup4 requests
```

### "OpenAI API key required"

Create `.env` file in project root:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Next Steps

- Explore [knowledge graph integration](../docs/knowledge_graph.md) (coming soon)
- See [advanced queries](../docs/advanced_queries.md) (coming soon)
- Learn about [custom embeddings](../docs/custom_embeddings.md) (coming soon)
