"""Voyage AI embedding generation."""

import os
from typing import List, Optional
from .base_embeddings import BaseEmbeddings


class VoyageEmbeddings(BaseEmbeddings):
    """Generate embeddings using Voyage AI API.

    Voyage AI offers high-quality embeddings optimized for retrieval:
    - voyage-3: Latest general-purpose model (1024 dimensions)
    - voyage-3-lite: Faster, cost-effective (512 dimensions)
    - voyage-code-3: Optimized for code (1024 dimensions)
    - voyage-finance-2: Domain-specific for finance (1024 dimensions)
    - voyage-law-2: Domain-specific for legal (1024 dimensions)
    """

    # Model dimensions mapping
    MODEL_DIMENSIONS = {
        "voyage-3": 1024,
        "voyage-3-lite": 512,
        "voyage-code-3": 1024,
        "voyage-finance-2": 1024,
        "voyage-law-2": 1024,
        "voyage-2": 1024,
        "voyage-lite-02-instruct": 1024,
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "voyage-3"):
        """
        Initialize Voyage embeddings.

        Args:
            api_key: Voyage API key (falls back to VOYAGE_API_KEY env var)
            model: Voyage model to use
        """
        try:
            import voyageai
        except ImportError:
            raise ImportError(
                "voyageai is required for Voyage embeddings. "
                "Install it with: uv add voyageai"
            )

        self.api_key = api_key or os.getenv("VOYAGE_API_KEY")
        self.model = model
        self.client = None

        if not self.api_key:
            raise ValueError(
                "Voyage API key required. Set VOYAGE_API_KEY or pass api_key to VoyageEmbeddings."
            )

        self.client = voyageai.Client(api_key=self.api_key)

    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        result = self.client.embed([text], model=self.model)
        return result.embeddings[0]

    def embed_batch(self, texts: List[str], batch_size: int = 128) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Voyage AI supports up to 128 texts per request.
        """
        embeddings: List[List[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            result = self.client.embed(batch, model=self.model)
            embeddings.extend(result.embeddings)

        return embeddings

    @property
    def dimension(self) -> int:
        """Return the dimension of the embedding vectors."""
        return self.MODEL_DIMENSIONS.get(self.model, 1024)

    @property
    def model_name(self) -> str:
        """Return the name of the embedding model."""
        return self.model
