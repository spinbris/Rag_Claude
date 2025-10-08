# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
# Install all dependencies
uv sync

# Install ragsystem package in editable mode
uv pip install -e .
```

### Step 2: Set up OpenAI API Key

Create a `.env` file in the project root:

```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### Step 3: Launch the Web Interface

**Option A: Auto-open browser (may show blank page on some systems)**
```bash
./start_gradio.sh
```

**Option B: Manual URL (recommended if browser shows blank page)**
```bash
./start_gradio.sh no-browser
```
Then copy the displayed URL and paste it into your browser.

The app will show you the URL (usually http://localhost:7860 or similar)

---

## 📁 Add Your Documents

### Option 1: Via Web Interface

1. Open the Gradio interface
2. Go to "📁 Data Management" tab
3. Place files in the `data/` folder
4. Click "Load from data/ folder"

### Option 2: Via Command Line

```bash
# Place files in data/ directory
cp your_document.pdf data/

# Run the loader script
uv run python examples/load_multiple_files.py
```

---

## 💬 Query Your Documents

### Via Web Interface

1. Go to "💬 Query Documents" tab
2. Type your question
3. Click "Ask Question"
4. View answer and sources

### Via Python

```python
from ragsystem import RAGSystem

rag = RAGSystem(persist_directory="outputs/chroma_db")
answer = rag.query("What is this document about?")
print(answer)
```

---

## 🛠️ Common Commands

| Task | Command |
|------|---------|
| Start Gradio UI | `./start_gradio.sh` |
| Stop Gradio UI | `./stop_gradio.sh` or `Ctrl+C` |
| Load multiple files | `uv run python examples/load_multiple_files.py` |
| Test setup | `uv run python tests/test_gradio.py` |
| Run tests | `uv run pytest` |

---

## 📊 Check Your Setup

```bash
uv run python tests/test_gradio.py
```

This will verify:
- ✓ Gradio is installed
- ✓ RAGSystem is available
- ✓ ChromaDB is connected
- ✓ Documents are loaded
- ✓ Queries work

---

## 🆘 Troubleshooting

### "Port already in use"

The app now automatically finds an available port. If you see this error:

```bash
./stop_gradio.sh
./start_gradio.sh
```

### "No documents in database"

Load some documents first:

```bash
# Via command line
uv run python examples/load_multiple_files.py

# Or via web interface (Data Management tab)
```

### "OpenAI API key required"

Make sure you have a `.env` file with your API key:

```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### "Module not found"

Install dependencies:

```bash
uv sync
```

---

## 📖 Learn More

- **[README.md](../README.md)** - System overview and features
- **[GRADIO_GUIDE.md](GRADIO_GUIDE.md)** - Complete Gradio interface guide
- **[examples/README.md](../examples/README.md)** - Code examples and tutorials

---

## 🎯 What Next?

1. **Explore the Examples:**
   ```bash
   ls examples/
   ```

2. **Try Different Queries:**
   - Use semantic search to explore your documents
   - Experiment with different `top_k` and `max_tokens` values
   - Save interesting results to files

3. **Add More Documents:**
   - Supports: PDF, DOCX, CSV, TXT, Markdown
   - Just drop files in `data/` and reload

4. **Organize Your Data:**
   - Create subdirectories in `data/`
   - Use different ChromaDB collections
   - See `examples/manage_collections.py`

---

**Happy querying! 🤖**
