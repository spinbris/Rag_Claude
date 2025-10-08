# Gradio Web Interface

This folder contains the Gradio web interface for the RAG System.

## 📁 Files

### Main Applications
- **gradio_app.py** - Main Gradio application (auto-opens browser)
- **gradio_app_no_browser.py** - Alternative version (manual URL)

### Launch Scripts
- **start_gradio.sh** - Start the Gradio interface
- **stop_gradio.sh** - Stop running Gradio processes

## 🚀 Quick Start

### From Project Root

**Start (auto-open browser):**
```bash
./start_gradio.sh
```

**Start (manual URL):**
```bash
./start_gradio.sh no-browser
```

**Stop:**
```bash
./stop_gradio.sh
```

### From This Folder

**Start:**
```bash
cd gradio
./start_gradio.sh
```

**Or directly (from project root):**
```bash
uv run python gradio/gradio_app.py
```

**Note:** Scripts automatically change to project root for proper imports.

## 📖 Documentation

See the [Gradio Guide](../guides/GRADIO_GUIDE.md) for complete documentation on:
- Using the interface
- All 4 tabs
- Parameters
- Best practices
- Troubleshooting

## 🛑 Exit Button

The Gradio interface includes an exit button that:
- Shuts down the server
- Closes the terminal automatically
- No need for Ctrl+C

See [Exit Button Guide](../guides/EXIT_BUTTON_INFO.md) for details.

## 🔧 Configuration

The Gradio app connects to:
- **ChromaDB:** `outputs/chroma_db/`
- **Default Port:** 7860 (auto-finds if busy)
- **Collections:** Configurable in code

## 📝 Files Explained

### gradio_app.py

Main application with:
- Auto browser opening
- 4 interactive tabs (Query, Search, Data Management, Help)
- Real-time stats
- Exit button
- Port auto-detection

### gradio_app_no_browser.py

Alternative version that:
- Doesn't auto-open browser
- Displays URL to copy/paste
- Useful if auto-open shows blank page

### start_gradio.sh

Launch script that:
- Accepts `no-browser` flag
- Shows helpful messages
- Runs appropriate app version
- Automatically changes to project root for imports
- Can be run from project root or gradio/ folder

### stop_gradio.sh

Stop script that:
- Finds all Gradio processes
- Kills processes on ports 7860-7869
- Cleans up properly

## 🌐 URL

The interface runs at:
- `http://localhost:7860` (or next available port)
- URL is displayed in terminal on startup
- Browser opens automatically (unless no-browser mode)

## 🔗 Related Files

- Root launchers: `../start_gradio.sh`, `../stop_gradio.sh`
- Documentation: `../guides/GRADIO_GUIDE.md`
- Tests: `../tests/test_gradio.py`

---

**For full documentation, see [guides/GRADIO_GUIDE.md](../guides/GRADIO_GUIDE.md)**
