"""Local embedding generation using Sentence Transformers."""

import os
from typing import List, Optional
from .base_embeddings import BaseEmbeddings


class SentenceTransformerEmbeddings(BaseEmbeddings):
    """Generate embeddings using local Sentence Transformer models.

    Popular models:
    - all-MiniLM-L6-v2: Fast, lightweight (384 dimensions)
    - all-mpnet-base-v2: Better quality (768 dimensions)
    - multi-qa-mpnet-base-dot-v1: Optimized for Q&A (768 dimensions)
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: Optional[str] = None):
        """
        Initialize Sentence Transformer embeddings.

        Args:
            model_name: HuggingFace model name
            device: Device to run on ('cuda', 'cpu', or None for auto)
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for local embeddings. "
                "Install it with: uv add sentence-transformers"
            )

        self._model_name = model_name
        self.device = device
        self.model = SentenceTransformer(model_name, device=device)

        # Get embedding dimension from model
        self._dimension = self.model.get_sentence_embedding_dimension()

    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Note: batch_size is typically smaller for local models due to memory constraints.
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 100
        )
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """Return the dimension of the embedding vectors."""
        return self._dimension

    @property
    def model_name(self) -> str:
        """Return the name of the embedding model."""
        return self._model_name
