RAGSystem
==========

This repository provides a small Retrieval-Augmented Generation (RAG) system.

Quick start for loading multiple documents

1. Create a `data/` directory at the project root and drop files inside (PDF, .docx, .md, .txt, .csv).
2. Use the library to load all files from the directory:

```python
from ragsystem import RAGSystem

rag = RAGSystem()
# Walks data/ and loads supported files. For a summary use verbose=True:
summary = rag.load_file('data/', verbose=True)
print(f"Added {summary['added_chunks']} chunks from data/")
if summary['skipped_files']:
	print("Skipped files:", summary['skipped_files'])

# Save index
rag.save('rag_index.pkl')
```

Notes:
- `RAGSystem.load_file` accepts a directory path and will recurse into subdirectories.
- Unsupported file types are skipped.
