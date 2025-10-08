"""ChromaDB-based vector storage with similarity search."""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import uuid


class ChromaVectorStore:
    """Vector store using ChromaDB for persistent storage."""

    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "rag_documents"):
        """
        Initialize ChromaDB vector store.

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection to use
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

    def add_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        """
        Add documents with their embeddings to the vector store.

        Args:
            documents: List of document dictionaries with 'content', 'source', 'type'
            embeddings: List of embedding vectors
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")

        if not documents:
            return

        # Generate unique IDs for each document
        ids = [str(uuid.uuid4()) for _ in documents]

        # Extract content for ChromaDB (required field)
        contents = [doc['content'] for doc in documents]

        # Store metadata (source, type, etc.)
        metadatas = [
            {
                'source': doc.get('source', 'unknown'),
                'type': doc.get('type', 'text')
            }
            for doc in documents
        ]

        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Search for similar documents using query embedding.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return

        Returns:
            List of documents with similarity scores
        """
        # Check if collection is empty
        if self.collection.count() == 0:
            return []

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count())
        )

        # Format results to match original VectorStore interface
        formatted_results = []

        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                result = {
                    'content': results['documents'][0][i],
                    'source': results['metadatas'][0][i].get('source', 'unknown'),
                    'type': results['metadatas'][0][i].get('type', 'text'),
                    'score': 1 - results['distances'][0][i]  # Convert distance to similarity
                }
                formatted_results.append(result)

        return formatted_results

    def save(self, filepath: str = None):
        """
        Save is handled automatically by ChromaDB persistence.
        This method is kept for API compatibility.

        Args:
            filepath: Ignored - ChromaDB uses persist_directory from __init__
        """
        # ChromaDB automatically persists changes
        # No action needed, but we can log for compatibility
        print(f"ChromaDB data automatically persisted to {self.persist_directory}")

    def load(self, filepath: str = None):
        """
        Load is handled automatically by ChromaDB.
        This method is kept for API compatibility.

        Args:
            filepath: Ignored - ChromaDB uses persist_directory from __init__
        """
        # ChromaDB automatically loads from persist_directory
        # Reload the collection to ensure it's current
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"ChromaDB collection '{self.collection_name}' loaded from {self.persist_directory}")

    def clear(self):
        """Clear all documents from the collection."""
        # Delete and recreate the collection
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def __len__(self):
        """Return the number of documents in the collection."""
        return self.collection.count()

    def get_collections(self) -> List[str]:
        """Get list of all collections in the database."""
        collections = self.client.list_collections()
        return [col.name for col in collections]

    def delete_collection(self, collection_name: str = None):
        """
        Delete a specific collection or the current one.

        Args:
            collection_name: Name of collection to delete (defaults to current)
        """
        name = collection_name or self.collection_name
        self.client.delete_collection(name=name)

        # If we deleted the current collection, recreate it
        if name == self.collection_name:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
