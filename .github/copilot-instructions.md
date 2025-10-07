## Quick orientation for AI coding agents

This repository implements a small Retrieval-Augmented Generation (RAG) system using OpenAI APIs. The goal of these instructions is to give an AI agent immediate, actionable knowledge about the project layout, conventions, and developer workflows so it can make safe, correct, and useful edits.

Key files and directories to reference:
- `rag.py` — main RAGSystem implementation (chunking, embedding, vector store, LLM calls).
- `loaders/` — source-specific loaders that return documents as dicts with `content`, `source`, `type` (see `loaders/base.py` and `loaders/pdf_loader.py`).
- `chunkers/text_chunker.py` — chunking policy (chunk_size, chunk_overlap) and sentence-boundary heuristics.
- `embeddings/openai_embeddings.py` — wraps OpenAI embeddings API. Expects `OPENAI_API_KEY` or explicit key passed in constructor.
- `storage/vector_storage.py` — in-memory numpy-based storage + similarity search using cosine similarity; supports `save`/`load` with pickle.
- `examples/basic_usage` — shows common usage flows (load, save, query, search).

Big picture / architecture notes
- The system consists of three main pipeline stages:
  1. Loaders: convert file/URL -> List[Dict] documents with `content`.
  2. Chunker: split large `content` strings into overlapping text chunks (`TextChunker.chunk`).
  3. Embeddings + VectorStore: create embeddings (`OpenAIEmbeddings`) and store them in `VectorStore` for similarity search. `RAGSystem.query` then retrieves top-k and calls OpenAI chat completions.
- Data passed between components: documents are dicts with keys `content`, `source`, `type`. Embeddings are lists of floats aligned one-to-one with chunks.
- The vector store is simple, in-memory, and persisted via `pickle` files using `VectorStore.save`/`load`.

-Developer workflows & commands
- Python version: `>=3.12` as declared in `pyproject.toml`.
 - Dependency management: prefer using `uv` + `pyproject.toml` + `uv.lock` as the source-of-truth.
   - Add new dependencies with `uv add <package>` which will update `pyproject.toml` and `uv.lock`.
   - For reproducible installs use `uv` to restore from `uv.lock` on CI or other machines.
   - CI note: GitHub Actions will perform a one-time bootstrap step to install `uv` via pip, then run `uv install` to restore from `uv.lock` (this keeps dependency resolution reproducible while only using pip once to install `uv`).
   - If contributors need a quick local install without `uv`, they can create a virtualenv and `pip install` the packages listed under `pyproject.toml`'s `dependencies`.
- Running the example: run the `examples/basic_usage` script or `python main.py` for the simple greeting.
- Running the example: run the `examples/basic_usage` script or `python main.py` for the simple greeting.
- Tests: none present. Keep changes small and run a quick smoke by invoking the example usage or a small script that instantiates `RAGSystem` and calls `chunker.chunk` and `VectorStore.add_documents`.

Project-specific conventions and patterns
- Loader interface: every loader implements `load(source: str) -> List[Dict]` returning at least `content`, `source`, `type`. Respect and preserve these keys when adding fields.
- Chunker contract: `TextChunker.chunk` returns list of strings; it silently returns `[]` for empty input. Minimum chunk length is enforced (50 chars).
- Embeddings: `OpenAIEmbeddings.__init__` will raise if `OPENAI_API_KEY` is not available. Code often passes api_key through `RAGSystem` which then instantiates `OpenAIEmbeddings`.
- VectorStore: expects embedding vectors aligned to document chunks. It stores embeddings as a numpy array and uses `cosine_similarity` from `sklearn.metrics.pairwise`.

Integration points / external dependencies
- OpenAI: used for both embeddings and chat/completions via the `openai` python client. Look at `embeddings/openai_embeddings.py` and `rag.py` for usage patterns. Keep API usage consistent (batch embeddings via `embed_batch`, single via `embed`).
- pypdf: used by `loaders/pdf_loader.py` to extract text.
- sklearn / numpy / pickle: used by `storage/vector_storage.py`.

Safe editing rules for AI agents
- Do not change the public data contract between components: documents must be dicts with `content`, `source`, and `type` unless you update all call sites.
- Preserve the chunking semantics: chunk size, overlap values, and the sentence-boundary heuristic. If proposing different chunking, include tests or a migration plan.
- When touching embeddings or OpenAI usage, keep the `api_key` handling and model name parameters visible in constructors; do not hardcode keys or new default models.
- For persistence, continue using `pickle` for `VectorStore.save/load` unless replacing it with a clear migration path and tests.

Concrete examples to copy from
- Creating and using system (from `examples/basic_usage`): instantiate `RAGSystem()`, call `load_*` methods, `save("rag_index.pkl")`, `query(question)`.
- Loader example (`loaders/pdf_loader.py`): return `[{ 'content': text, 'source': filepath, 'type': 'pdf' }]` or raise `ValueError` on errors.

Search & refactor guidance
- Make small, localized changes. Run the example usage as a smoke test.
- If adding new loader types, implement `BaseLoader`, add constructor wiring in `RAGSystem.__init__`, and update `RAGSystem.load_file` mapping.

Questions for the maintainer
- Are there preferred test frameworks or CI steps you want agents to add? (none found in repo)
- Should persistent storage move off pickle to a more robust store (faiss/annoy/sql)? If so, point to preferred library and migration guidance.

If anything in these instructions is unclear or you want more/less detail, tell me which files or workflows to expand and I'll update this file.
