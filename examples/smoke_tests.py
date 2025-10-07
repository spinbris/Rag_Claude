
"""Reusable smoke tests for quick local checks.

Three tests provided as functions so they can be invoked individually or from CI:
- minimal_smoke(): runs the `main.py` entry to confirm no syntax/import errors.
- functional_smoke(): exercises `TextChunker` and `VectorStore` (offline, requires numpy & scikit-learn).
- rag_instantiate_smoke(): instantiates `RAGSystem` without making network calls (conservative).

Run examples from project root:
  python examples/smoke_tests.py --minimal
  python examples/smoke_tests.py --functional
  python examples/smoke_tests.py --rag
"""

from __future__ import annotations

import argparse
import importlib
import runpy
import os
from typing import Any


def minimal_smoke() -> bool:
	"""Run the package entry point `main.py` to ensure it executes without syntax/import errors.

	Returns True on success, False on failure.
	"""
	try:
		# runpy.run_path will execute the file as __main__ without importing package
		runpy.run_path(os.path.join(os.path.dirname(__file__), "..", "main.py"), run_name="__main__")
		print("minimal_smoke: OK")
		return True
	except Exception as e:
		print(f"minimal_smoke: FAIL - {e}")
		return False


def functional_smoke() -> bool:
	"""Test TextChunker and VectorStore basic behavior.

	This is an offline test but requires numpy and scikit-learn to be installed.
	Returns True on success, False on failure.
	"""
	try:
		from chunkers.text_chunker import TextChunker
		from storage.vector_storage import VectorStore

		# Chunk some text
		c = TextChunker()
		chunks = c.chunk("This is a sample sentence. " * 20)
		if not chunks:
			print("functional_smoke: FAIL - no chunks produced")
			return False

		# Create deterministic fake embeddings (small dim) and add to vector store
		dim = 8
		embs = [[float((i + j) % dim) for j in range(dim)] for i, _ in enumerate(chunks)]
		docs = [{"content": ch, "source": "inline", "type": "text"} for ch in chunks]

		vs = VectorStore()
		vs.add_documents(docs, embs)

		if len(vs) != len(docs):
			print(f"functional_smoke: FAIL - stored {len(vs)} docs, expected {len(docs)}")
			return False

		# Ensure search returns results
		results = vs.search(embs[0], top_k=1)
		if not results:
			print("functional_smoke: FAIL - search returned no results")
			return False

		print("functional_smoke: OK")
		return True
	except Exception as e:
		print(f"functional_smoke: FAIL - {e}")
		return False


def rag_instantiate_smoke() -> bool:
	"""Instantiate RAGSystem without making network calls.

	This checks construction and attribute access only.
	"""
	try:
		# Import lazily to avoid side-effects during module import
		from rag import RAGSystem

		# construct with default args (do not require an API key for instantiation)
		rs = RAGSystem()
		# Basic sanity checks
		_ = rs.chunker.chunk_size
		_ = rs.vector_store
		print("rag_instantiate_smoke: OK")
		return True
	except Exception as e:
		print(f"rag_instantiate_smoke: FAIL - {e}")
		return False


def main(argv: list[str] | None = None) -> int:
	parser = argparse.ArgumentParser()
	parser.add_argument("--minimal", action="store_true")
	parser.add_argument("--functional", action="store_true")
	parser.add_argument("--rag", action="store_true")

	args = parser.parse_args(argv)

	if args.minimal:
		return 0 if minimal_smoke() else 2
	if args.functional:
		return 0 if functional_smoke() else 2
	if args.rag:
		return 0 if rag_instantiate_smoke() else 2

	# Default: run all three, fail on first error
	if not minimal_smoke():
		return 2
	if not functional_smoke():
		return 2
	if not rag_instantiate_smoke():
		return 2

	print("All smoke tests passed")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

