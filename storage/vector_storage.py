
"""Vector storage with similarity search."""

import numpy as np
import pickle
from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity


class VectorStore:
    """Store and search document embeddings."""
    
    def __init__(self):
        """Initialize vector store."""
        self.documents = []
        self.embeddings = None
    
    def add_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        """
        Add documents and their embeddings to the store.
        
        Args:
            documents: List of document dictionaries
            embeddings: List of embedding vectors
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        self.documents.extend(documents)
        
        new_embeddings = np.array(embeddings)
        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Search for most similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of documents with similarity scores
        """
        if self.embeddings is None or len(self.embeddings) == 0:
            return []
        
        query_embedding = np.array([query_embedding])
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        top_k = min(top_k, len(similarities))
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            result = self.documents[idx].copy()
            result['score'] = float(similarities[idx])
            results.append(result)
        
        return results
    
    def save(self, filepath: str):
        """Save vector store to disk."""
        data = {
            'documents': self.documents,
            'embeddings': self.embeddings.tolist() if self.embeddings is not None else None
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, filepath: str):
        """Load vector store from disk."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        self.documents = data['documents']
        self.embeddings = np.array(data['embeddings']) if data['embeddings'] else None
    
    def clear(self):
        """Clear all documents and embeddings."""
        self.documents = []
        self.embeddings = None
    
    def __len__(self):
        """Return number of documents in store."""
        return len(self.documents)
