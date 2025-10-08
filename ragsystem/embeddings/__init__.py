"""Re-export embeddings from the project's top-level `embeddings` package.

This avoids duplicating the implementation and ensures tests that import
`embeddings.openai_embeddings.OpenAIEmbeddings` can monkeypatch the same
class used by `ragsystem`.
"""
from embeddings.openai_embeddings import OpenAIEmbeddings

__all__ = ["OpenAIEmbeddings"]
