"""Test knowledge graph functionality."""

import pytest
from ragsystem.graph_rag import GraphRAGSystem
from ragsystem.knowledge_graph import KnowledgeGraphExtractor, GraphEnhancedStorage, GraphVisualizer


def test_graph_extractor_pattern_based():
    """Test pattern-based entity and relation extraction."""
    extractor = KnowledgeGraphExtractor(api_key=None)

    text = "Python is a programming language. Python was created by Guido van Rossum."

    result = extractor.extract_entities_and_relations(text, use_llm=False)

    assert 'entities' in result
    assert 'relations' in result
    assert len(result['entities']) > 0


def test_graph_metadata_builder():
    """Test building graph metadata for a chunk."""
    extractor = KnowledgeGraphExtractor(api_key=None)

    text = "Python is a programming language used for machine learning."
    chunk_id = "test_chunk_1"

    metadata = extractor.build_graph_metadata(text, chunk_id)

    assert metadata['chunk_id'] == chunk_id
    assert 'entities' in metadata
    assert 'relations' in metadata
    assert 'keywords' in metadata
    assert isinstance(metadata['has_graph_data'], bool)


def test_graph_enhanced_storage():
    """Test graph-enhanced storage operations."""
    storage = GraphEnhancedStorage(
        persist_directory="./test_graph_db",
        collection_name="test_graph_collection"
    )

    # Clean up before test
    storage.clear()

    # Create test data
    documents = [
        {"content": "Python is a programming language.", "source": "test.txt", "type": "text"}
    ]

    # Create dummy embeddings (384 dimensions for all-MiniLM-L6-v2)
    embeddings = [[0.1] * 384]

    # Create graph metadata
    graph_metadata = [{
        "entities": ["Python", "programming language"],
        "entity_types": ["technology", "concept"],
        "relations": ["Python|is_a|programming language"],
        "keywords": ["python", "programming"],
        "has_graph_data": True
    }]

    # Add documents
    storage.add_documents_with_graph(documents, embeddings, graph_metadata)

    assert len(storage) == 1

    # Search by entity
    results = storage.find_by_entity("Python", top_k=5)
    assert len(results) > 0
    assert "Python" in results[0]['graph']['entities']

    # Clean up
    storage.clear()


def test_visualizer_ascii():
    """Test ASCII art visualization."""
    entities = {"Python": 5, "Java": 3, "C++": 2}
    relations = [
        ("Python", "is_a", "programming language"),
        ("Java", "is_a", "programming language")
    ]

    ascii_art = GraphVisualizer.to_ascii_art(entities, relations, max_entities=10)

    assert isinstance(ascii_art, str)
    assert "Python" in ascii_art
    assert "Java" in ascii_art


def test_visualizer_mermaid():
    """Test Mermaid diagram generation."""
    entities = ["Python", "Java", "programming language"]
    relations = [
        ("Python", "is_a", "programming language"),
        ("Java", "is_a", "programming language")
    ]

    mermaid = GraphVisualizer.to_mermaid(entities, relations)

    assert isinstance(mermaid, str)
    assert "graph TD" in mermaid
    assert "Python" in mermaid
    assert "is_a" in mermaid


def test_visualizer_cytoscape():
    """Test Cytoscape.js format generation."""
    entities = ["Python", "Java"]
    relations = [("Python", "similar_to", "Java")]

    cyto_data = GraphVisualizer.to_cytoscape(entities, relations)

    assert 'nodes' in cyto_data
    assert 'edges' in cyto_data
    assert len(cyto_data['nodes']) == 2
    assert len(cyto_data['edges']) == 1


def test_graph_rag_initialization():
    """Test GraphRAGSystem initialization."""
    # Test with default settings (without actually loading data)
    graph_rag = GraphRAGSystem(
        api_key="fake_key",
        enable_graph_extraction=False,  # Disable to avoid LLM calls
        persist_directory="./test_graph_rag_db",
        collection_name="test_rag"
    )

    assert graph_rag.enable_graph_extraction is False
    assert graph_rag.graph_extractor is None
    assert graph_rag.embeddings is not None


def test_graph_rag_with_custom_embeddings():
    """Test GraphRAGSystem with custom embedding provider."""
    try:
        from embeddings import SentenceTransformerEmbeddings

        local_emb = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")

        graph_rag = GraphRAGSystem(
            embeddings=local_emb,
            enable_graph_extraction=False,
            persist_directory="./test_graph_custom_emb",
            collection_name="test_custom"
        )

        assert graph_rag.embeddings.model_name == "all-MiniLM-L6-v2"
        assert graph_rag.embeddings.dimension == 384

    except ImportError:
        pytest.skip("sentence-transformers not installed")
