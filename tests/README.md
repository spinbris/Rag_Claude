# Tests Folder

This folder contains all test scripts for the RAG System.

## 📁 Test Files

### System Tests
- **test_smoke.py** - Comprehensive smoke tests for all major components
- **test_gradio.py** - Gradio interface availability and functionality tests
- **test_persistence.py** - ChromaDB persistence and data retention tests

### Integration Tests
- **test_integration_data_load.py** - Tests for loading documents from data/ folder
- **test_summary.py** - Tests for PDF loading and document summarization

## 🚀 Running Tests

### Run All Tests
```bash
uv run pytest
```

### Run Specific Test
```bash
uv run python tests/test_gradio.py
uv run python tests/test_smoke.py
uv run python tests/test_summary.py
```

### Run with Verbose Output
```bash
uv run pytest -v
```

### Run Specific Test File
```bash
uv run pytest tests/test_smoke.py
```

## 📝 Test Descriptions

### test_smoke.py
**Comprehensive smoke tests covering:**
- RAG system initialization
- Document loading (PDF, TXT, CSV, DOCX, MD)
- Vector storage operations
- Query functionality
- Search functionality
- Stats retrieval
- Collection management

**Usage:**
```bash
uv run python tests/test_smoke.py
```

### test_gradio.py
**Tests Gradio interface components:**
- Gradio installation
- RAGSystem availability
- ChromaDB connection
- Interface initialization

**Usage:**
```bash
uv run python tests/test_gradio.py
```

### test_persistence.py
**Tests data persistence:**
- Saving to ChromaDB
- Loading from ChromaDB
- Data retention across sessions
- Collection persistence

**Usage:**
```bash
uv run python tests/test_persistence.py
```

### test_integration_data_load.py
**Tests loading documents from data/ folder:**
- Loading multiple files
- Different file formats
- Summary statistics

**Usage:**
```bash
uv run python tests/test_integration_data_load.py
```

### test_summary.py
**Tests PDF summarization:**
- PDF loading
- Summary generation
- Output file creation
- Timestamps

**Usage:**
```bash
uv run python tests/test_summary.py
```

## 📊 Test Output

All test outputs are saved to the `outputs/` folder:
- Summary files: `outputs/summary_*.txt`
- Query results: `outputs/query_*.txt`
- Analysis reports: `outputs/multi_file_analysis_*.txt`

## 🧪 Test Data

Tests use documents from the `data/` folder:
- `data/CPG229.pdf` - Sample PDF for testing
- Other test documents as needed

## 🔧 Configuration

Tests use:
- **ChromaDB:** `outputs/chroma_db/`
- **Test Collections:** Various test collection names
- **OpenAI Models:** text-embedding-3-small, gpt-4o-mini

Make sure your `.env` file has a valid `OPENAI_API_KEY` before running tests.

## ✅ Test Coverage

Current test coverage includes:
- ✓ Document loading (all formats)
- ✓ Vector storage operations
- ✓ Query and search functionality
- ✓ Persistence and data retention
- ✓ Collection management
- ✓ Gradio interface availability
- ✓ Summary generation

## 🆘 Troubleshooting

### "OpenAI API key required"
Make sure you have a `.env` file with your API key:
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### "No module named 'ragsystem'"
Run from the project root:
```bash
cd /path/to/Rag_Claude
uv run python tests/test_smoke.py
```

### "ChromaDB already exists"
Tests create temporary collections. If you get errors about existing collections:
```bash
rm -rf outputs/chroma_db/
```

---

**For more information, see the main [README.md](../README.md)**
