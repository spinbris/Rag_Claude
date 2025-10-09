"""Re-export embeddings from the project's top-level `embeddings` package.

This avoids duplicating the implementation and ensures tests that import
`embeddings.openai_embeddings.OpenAIEmbeddings` can monkeypatch the same
class used by `ragsystem`.
"""
from embeddings.base_embeddings import BaseEmbeddings
from embeddings.openai_embeddings import OpenAIEmbeddings
from embeddings.sentence_transformer_embeddings import SentenceTransformerEmbeddings
from embeddings.voyage_embeddings import VoyageEmbeddings

__all__ = [
    "BaseEmbeddings",
    "OpenAIEmbeddings",
    "SentenceTransformerEmbeddings",
    "VoyageEmbeddings",
]
