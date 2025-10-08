
"""Compatibility shim: re-export VectorStore from `ragsystem` package."""

from ragsystem.storage.vector_storage import VectorStore

__all__ = ["VectorStore"]
