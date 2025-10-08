# Gradio Web Interface Guide

## Quick Start

### 1. Launch the Interface

```bash
./start_gradio.sh
```

Or manually:

```bash
uv run python gradio/gradio_app.py
```

### 2. Open in Browser

Navigate to: **http://localhost:7860**

---

## Interface Overview

The Gradio interface has 4 main tabs:

### 💬 Query Documents Tab

**Ask questions about your documents using natural language.**

**Features:**
- Text input for your questions
- Adjustable parameters:
  - **top_k**: Number of document chunks to retrieve (1-20, default: 5)
  - **max_tokens**: Maximum response length (100-1000, default: 500)
- Option to save results to file
- Real-time database statistics
- Example questions to get started

**Example Questions:**
- "What is the main topic of these documents?"
- "What are the key recommendations?"
- "Summarize the governance requirements."
- "What climate-related risks are mentioned?"

**How It Works:**
1. Enter your question
2. Adjust parameters if needed
3. Click "🔍 Ask Question"
4. View the answer and source citations
5. Optionally save the result to `outputs/query_*.txt`

---

### 🔍 Semantic Search Tab

**Search for relevant document chunks without LLM generation.**

**Use Cases:**
- Find specific topics or keywords
- Explore what's in your database
- Quick reference lookup
- See exact document excerpts

**Features:**
- Fast semantic similarity search
- Adjustable number of results (1-20)
- Shows similarity scores
- Displays full chunk content

**Example Searches:**
- "climate change risks"
- "board responsibilities"
- "disclosure requirements"
- "scenario analysis"

---

### 📁 Data Management Tab

**Load and manage documents in ChromaDB.**

**Features:**
- Load all documents from `data/` directory
- See loading progress and statistics
- View skipped files and errors
- Information about current database

**How to Load Documents:**
1. Place files in the `data/` directory
2. Click "📂 Load from data/ folder"
3. Wait for processing (may take a few minutes)
4. Check the results

**Supported File Types:**
- PDF (`.pdf`)
- Word Documents (`.docx`, `.doc`)
- CSV (`.csv`)
- Text files (`.txt`)
- Markdown (`.md`, `.markdown`)

---

### ❓ Help Tab

**Complete documentation and troubleshooting guide.**

Contains:
- Detailed usage instructions
- Parameter explanations
- Tips and best practices
- Troubleshooting guide
- File locations

---

## Parameters Explained

### top_k (Number of Chunks)

**What it does:** Controls how many document chunks are retrieved from the database.

**When to adjust:**
- **Lower (1-3)**: Quick, specific questions
- **Medium (5-7)**: General questions (default)
- **Higher (10-20)**: Complex questions needing lots of context

**Trade-offs:**
- More chunks = more context = better answers for complex questions
- More chunks = slower processing = higher API costs

### max_tokens (Response Length)

**What it does:** Limits the length of the AI's response.

**When to adjust:**
- **Short (100-200)**: Brief answers, summaries
- **Medium (300-500)**: Detailed explanations (default)
- **Long (600-1000)**: Comprehensive answers, multiple points

**Trade-offs:**
- More tokens = longer, more detailed responses
- More tokens = higher API costs

---

## Database Statistics

The stats panel shows:

- **Total Documents**: Number of text chunks stored
- **Chunk Size**: Maximum characters per chunk (default: 1000)
- **Chunk Overlap**: Overlapping characters between chunks (default: 200)
- **Embedding Model**: AI model used for embeddings (default: text-embedding-3-small)
- **LLM Model**: AI model used for answers (default: gpt-4o-mini)
- **Available Collections**: Separate document namespaces
- **Storage Location**: Where ChromaDB data is stored

---

## Tips & Best Practices

### 📝 Writing Good Questions

✅ **Good Questions:**
- "What are the main climate risks discussed?"
- "Summarize the governance framework"
- "Who is responsible for risk management?"

❌ **Poor Questions:**
- "Tell me everything" (too broad)
- "Yes or no" (needs context)
- Very vague or ambiguous

### 🎯 Optimizing Retrieval

**For Specific Information:**
- Use lower top_k (3-5)
- Use specific keywords in your question
- Try semantic search first to explore

**For Complex Analysis:**
- Use higher top_k (10-15)
- Ask focused questions
- Break complex questions into parts

### 💾 Saving Results

Enable "Save result to file" to:
- Keep a record of important queries
- Share findings with others
- Build a knowledge base over time

Files are saved to: `outputs/query_YYYYMMDD_HHMMSS.txt`

### 🔄 Refreshing Stats

Click "🔄 Refresh Stats" after:
- Loading new documents
- Clearing collections
- Making any database changes

---

## Troubleshooting

### "No documents in database"

**Solution:**
1. Go to "Data Management" tab
2. Ensure files are in `data/` directory
3. Click "Load from data/ folder"
4. Wait for completion

### "RAG system not initialized"

**Solution:**
- Refresh the browser page
- Check that ChromaDB directory exists
- Verify permissions on `outputs/` folder

### Slow Responses

**Causes:**
- Large top_k value
- High max_tokens
- Complex documents
- Network latency to OpenAI

**Solutions:**
- Reduce top_k to 3-5
- Reduce max_tokens to 300-400
- Check your internet connection

### Empty Search Results

**Causes:**
- No relevant documents in database
- Query too specific
- Documents not loaded properly

**Solutions:**
- Try broader search terms
- Verify documents loaded successfully
- Check database stats

### API Errors

**Common Issues:**
- Invalid OpenAI API key
- API rate limits exceeded
- Network connectivity

**Solutions:**
- Verify `.env` file has correct `OPENAI_API_KEY`
- Wait a moment and retry
- Check OpenAI dashboard for quota/limits

### Browser Shows Blank Page

**Problem:** Browser opens to `about:blank` or blank screen

**Solutions:**

**Option 1: Use manual URL mode**
```bash
./stop_gradio.sh
./start_gradio.sh no-browser
```
Copy the displayed URL (e.g., `http://localhost:7860`) and paste it into your browser.

**Option 2: Wait and refresh**
- The server might still be starting
- Wait 5-10 seconds
- Refresh the browser page
- Or manually visit `http://localhost:7860`

**Option 3: Check the port**
- The app auto-finds available ports (7860-7869)
- Check the console output for the actual URL
- Make sure to use the correct port number

---

## Advanced Usage

### Multiple Collections

To query different collections, you'll need to modify the code or use the Python API:

```python
from ragsystem import RAGSystem

# Query collection 1
rag1 = RAGSystem(persist_directory="outputs/chroma_db", collection_name="finance")
answer1 = rag1.query("What are the financial metrics?")

# Query collection 2
rag2 = RAGSystem(persist_directory="outputs/chroma_db", collection_name="research")
answer2 = rag2.query("What are the research findings?")
```

### Programmatic Access

For automation and scripts, see the examples in `examples/`:
- `load_multiple_files.py` - Batch loading
- `manage_collections.py` - Collection management
- `add_to_existing_collection.py` - Incremental loading

### Batch Queries

For processing multiple questions, create a Python script:

```python
from ragsystem import RAGSystem

rag = RAGSystem(persist_directory="outputs/chroma_db")

questions = [
    "What is the main topic?",
    "What are the key findings?",
    "Who are the authors?"
]

for q in questions:
    answer = rag.query(q)
    print(f"Q: {q}")
    print(f"A: {answer}\n")
```

---

## File Locations

| Type | Location |
|------|----------|
| **ChromaDB Database** | `outputs/chroma_db/` |
| **Query Results** | `outputs/query_*.txt` |
| **Input Documents** | `data/` |
| **Analysis Reports** | `outputs/multi_file_analysis_*.txt` |
| **Manifests** | `outputs/loaded_files_*.txt` |

---

## Security & Privacy

### Local Operation

- All processing happens locally except API calls to OpenAI
- ChromaDB data is stored on your machine
- No data shared with third parties (except OpenAI for embeddings/LLM)

### API Keys

- Keep your `.env` file secure
- Never commit API keys to version control
- Rotate keys regularly

### Data Retention

- ChromaDB persists all data until explicitly deleted
- Query results are saved as text files if you enable the option
- Clear collections to remove data: use examples or delete `outputs/chroma_db/`

---

## Shutting Down the Server

### Method 1: Exit Button (Easiest) ⭐

The **recommended** way to shut down:

1. Scroll to the bottom of the Gradio interface
2. Click the **"🛑 Exit & Shutdown Server"** button
3. Wait 2 seconds
4. **Terminal automatically closes** - No Ctrl+C needed!
5. Close the browser tab (if it doesn't auto-close)

**This is the cleanest method - the terminal will close itself!**

### Method 2: Keyboard Shortcut

In the terminal where the server is running:
- Press **Ctrl + C** (or **Cmd + C** on Mac)

### Method 3: Stop Script

From another terminal:
```bash
./stop_gradio.sh  # From project root
# Or from gradio folder:
cd gradio && ./stop_gradio.sh
```

---

## Keyboard Shortcuts

- **Shift + Enter** in question box: Submit query
- **Ctrl/Cmd + C** in terminal: Stop server immediately

---

## Getting Help

1. Check the **Help** tab in the interface
2. Review `examples/README.md` for code examples
3. See main `README.md` for system overview
4. Check error messages - they usually indicate the issue

---

## What's Next?

- Explore the examples in `examples/` folder
- Add more documents to expand your knowledge base
- Experiment with different parameter combinations
- Build custom workflows using the Python API

**Happy Querying! 🚀**
