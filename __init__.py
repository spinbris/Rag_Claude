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

from .rag import RAGSystem

__version__ = "1.0.0"
__all__ = ["RAGSystem"]
