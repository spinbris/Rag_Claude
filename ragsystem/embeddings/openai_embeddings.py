"""OpenAI embedding generation."""

import os
from typing import List, Optional
import openai


class OpenAIEmbeddings:
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
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
        self._ensure_client()
        response = self.client.embeddings.create(
            input=text,
            model=self.model,
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
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
