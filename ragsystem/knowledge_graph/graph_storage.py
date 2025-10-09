"""Graph-enhanced storage layer for ChromaDB."""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Set, Tuple
import uuid
import json


class GraphEnhancedStorage:
    """
    ChromaDB storage with knowledge graph capabilities.

    Works with ANY embedding provider - the embeddings are used for semantic search,
    while graph relationships are stored as metadata.
    """

    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "rag_graph"):
        """
        Initialize graph-enhanced storage.

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection to use
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Initialize ChromaDB client
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
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents_with_graph(
        self,
        documents: List[Dict],
        embeddings: List[List[float]],
        graph_metadata: Optional[List[Dict]] = None
    ):
        """
        Add documents with embeddings and graph metadata.

        Args:
            documents: List of document dicts with 'content', 'source', 'type'
            embeddings: List of embedding vectors (from ANY embedding provider)
            graph_metadata: Optional list of graph metadata dicts with:
                - entities: List of entity names
                - entity_types: List of entity types
                - relations: List of "source|relation|target" strings
                - keywords: List of keywords
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")

        if not documents:
            return

        # Generate unique IDs
        ids = [str(uuid.uuid4()) for _ in documents]

        # Extract content
        contents = [doc['content'] for doc in documents]

        # Build metadata
        metadatas = []
        for i, doc in enumerate(documents):
            metadata = {
                'source': doc.get('source', 'unknown'),
                'type': doc.get('type', 'text'),
                'chunk_id': ids[i]
            }

            # Add graph metadata if provided
            if graph_metadata and i < len(graph_metadata):
                graph_data = graph_metadata[i]
                metadata.update({
                    'entities': json.dumps(graph_data.get('entities', [])),
                    'entity_types': json.dumps(graph_data.get('entity_types', [])),
                    'relations': json.dumps(graph_data.get('relations', [])),
                    'keywords': json.dumps(graph_data.get('keywords', [])),
                    'has_graph': graph_data.get('has_graph_data', False)
                })

            metadatas.append(metadata)

        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )

    def search(self, query_embedding: List[float], top_k: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Semantic search using embeddings (works with any embedding provider).

        Args:
            query_embedding: Query vector (from ANY embedding provider)
            top_k: Number of results
            filter_dict: Optional metadata filters

        Returns:
            List of results with graph metadata
        """
        if self.collection.count() == 0:
            return []

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count()),
            where=filter_dict
        )

        # Format results with graph metadata
        formatted_results = []

        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                metadata = results['metadatas'][0][i]

                result = {
                    'content': results['documents'][0][i],
                    'source': metadata.get('source', 'unknown'),
                    'type': metadata.get('type', 'text'),
                    'score': 1 - results['distances'][0][i],
                    'chunk_id': metadata.get('chunk_id'),
                }

                # Parse graph metadata if present
                if metadata.get('has_graph'):
                    result['graph'] = {
                        'entities': json.loads(metadata.get('entities', '[]')),
                        'entity_types': json.loads(metadata.get('entity_types', '[]')),
                        'relations': json.loads(metadata.get('relations', '[]')),
                        'keywords': json.loads(metadata.get('keywords', '[]'))
                    }

                formatted_results.append(result)

        return formatted_results

    def find_by_entity(self, entity_name: str, top_k: int = 10) -> List[Dict]:
        """
        Find all chunks containing a specific entity.

        Args:
            entity_name: Name of the entity to search for
            top_k: Maximum number of results

        Returns:
            List of chunks containing the entity
        """
        # Get all documents
        all_docs = self.collection.get()

        results = []
        for i, metadata in enumerate(all_docs['metadatas']):
            if metadata.get('has_graph'):
                entities = json.loads(metadata.get('entities', '[]'))
                if entity_name in entities:
                    results.append({
                        'content': all_docs['documents'][i],
                        'source': metadata.get('source'),
                        'chunk_id': metadata.get('chunk_id'),
                        'graph': {
                            'entities': entities,
                            'entity_types': json.loads(metadata.get('entity_types', '[]')),
                            'relations': json.loads(metadata.get('relations', '[]'))
                        }
                    })

            if len(results) >= top_k:
                break

        return results

    def get_all_entities(self) -> Dict[str, int]:
        """
        Get all unique entities and their frequencies.

        Returns:
            Dict mapping entity names to occurrence counts
        """
        entity_counts = {}
        all_docs = self.collection.get()

        for metadata in all_docs['metadatas']:
            if metadata.get('has_graph'):
                entities = json.loads(metadata.get('entities', '[]'))
                for entity in entities:
                    entity_counts[entity] = entity_counts.get(entity, 0) + 1

        return entity_counts

    def get_all_relations(self) -> List[Tuple[str, str, str]]:
        """
        Get all unique relationships in the graph.

        Returns:
            List of (source, relation, target) tuples
        """
        relations_set: Set[Tuple[str, str, str]] = set()
        all_docs = self.collection.get()

        for metadata in all_docs['metadatas']:
            if metadata.get('has_graph'):
                relations = json.loads(metadata.get('relations', '[]'))
                for rel_str in relations:
                    parts = rel_str.split('|')
                    if len(parts) == 3:
                        relations_set.add(tuple(parts))

        return list(relations_set)

    def traverse_graph(self, start_entity: str, max_hops: int = 2) -> Dict:
        """
        Traverse the knowledge graph starting from an entity.

        Args:
            start_entity: Entity to start from
            max_hops: Maximum number of relationship hops

        Returns:
            Dict with entities and relations in the subgraph
        """
        entities_found = {start_entity}
        relations_found = []
        frontier = {start_entity}

        all_relations = self.get_all_relations()

        for hop in range(max_hops):
            new_entities = set()

            for source, relation, target in all_relations:
                if source in frontier:
                    new_entities.add(target)
                    relations_found.append((source, relation, target))
                elif target in frontier:
                    new_entities.add(source)
                    relations_found.append((source, relation, target))

            frontier = new_entities - entities_found
            entities_found.update(frontier)

            if not frontier:
                break

        return {
            "entities": list(entities_found),
            "relations": relations_found,
            "hops": hop + 1 if frontier else hop
        }

    def __len__(self):
        """Return the number of documents in the collection."""
        return self.collection.count()

    def clear(self):
        """Clear all documents from the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
