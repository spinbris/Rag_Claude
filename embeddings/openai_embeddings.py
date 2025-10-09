
"""OpenAI embedding generation."""

import os
from typing import List, Optional
import openai
from .base_embeddings import BaseEmbeddings


class OpenAIEmbeddings(BaseEmbeddings):
    """Generate embeddings using OpenAI API.

    The client is created lazily so modules can be imported/instantiated in
    environments without an API key. Attempting to use `embed` or
    `embed_batch` without an API key will raise a descriptive error.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        """Store configuration; client will be created on demand.

        Args:
            api_key: OpenAI API key (falls back to OPENAI_API_KEY env var)
            model: Embedding model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None

    def _ensure_client(self):
        if self.client is not None:
            return
        if not self.api_key:
            raise ValueError("OpenAI API key required to generate embeddings. Set OPENAI_API_KEY or pass api_key to OpenAIEmbeddings.")
        self.client = openai.OpenAI(api_key=self.api_key)

    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text.

        Raises a ValueError if no API key is configured.
        """
        self._ensure_client()
        response = self.client.embeddings.create(
            input=text,
            model=self.model,
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches."""
        self._ensure_client()
        embeddings: List[List[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self.client.embeddings.create(
                input=batch,
                model=self.model,
            )
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
        return embeddings

    @property
    def dimension(self) -> int:
        """Return the dimension of the embedding vectors."""
        # OpenAI text-embedding-3-small: 1536, text-embedding-3-large: 3072
        if "large" in self.model:
            return 3072
        return 1536

    @property
    def model_name(self) -> str:
        """Return the name of the embedding model."""
        return self.model