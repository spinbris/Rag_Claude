"""RAG System - Retrieval Augmented Generation with Web and PDF support.

This package will attempt to load a `.env` file on import using python-dotenv
so environment variables like `OPENAI_API_KEY` become available to all modules.
The import is defensive: if `python-dotenv` is not installed the package falls
back to the existing environment.
"""

try:
	from dotenv import load_dotenv

	load_dotenv(override=True)
except ImportError:
	# If python-dotenv is not installed, continue without raising.
	pass

# Do not import subpackages at module import time; importing the top-level
# package during test collection caused heavy imports (requests, pypdf, etc.)
# Tests should import specific modules (e.g. `from ragsystem import RAGSystem`) when needed.
__version__ = "1.0.0"
__all__ = []
