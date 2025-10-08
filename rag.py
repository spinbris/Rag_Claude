
"""Main RAG system implementation."""

# Ensure environment variables from .env are available to all consumers that
# import this module. This is defensive: if python-dotenv is not installed we
# silently continue and rely on the existing environment.
try:
    from dotenv import load_dotenv

    load_dotenv(override=True)
except ImportError:
    pass

"""Compatibility shim: re-export RAGSystem from the new `ragsystem` package."""

from ragsystem.rag import RAGSystem

__all__ = ["RAGSystem"]

