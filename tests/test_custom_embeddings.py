"""Test custom embedding implementations."""

import pytest
from embeddings import (
    BaseEmbeddings,
    OpenAIEmbeddings,
    SentenceTransformerEmbeddings,
    VoyageEmbeddings,
)


def test_openai_embeddings_implements_base():
    """Test that OpenAIEmbeddings properly implements BaseEmbeddings."""
    assert issubclass(OpenAIEmbeddings, BaseEmbeddings)

    # Test instantiation (won't actually call API without key)
    embeddings = OpenAIEmbeddings(api_key="fake_key")

    # Test properties exist
    assert hasattr(embeddings, 'dimension')
    assert hasattr(embeddings, 'model_name')
    assert embeddings.dimension in [1536, 3072]
    assert embeddings.model_name == "text-embedding-3-small"


def test_sentence_transformer_embeddings_implements_base():
    """Test that SentenceTransformerEmbeddings implements BaseEmbeddings."""
    assert issubclass(SentenceTransformerEmbeddings, BaseEmbeddings)


def test_voyage_embeddings_implements_base():
    """Test that VoyageEmbeddings implements BaseEmbeddings."""
    assert issubclass(VoyageEmbeddings, BaseEmbeddings)


def test_sentence_transformer_local_embedding():
    """Test local sentence transformer embedding generation."""
    try:
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

        # Test single embedding
        text = "This is a test sentence."
        embedding = embeddings.embed(text)

        assert isinstance(embedding, list)
        assert len(embedding) == embeddings.dimension
        assert embeddings.dimension == 384  # all-MiniLM-L6-v2 dimension
        assert embeddings.model_name == "all-MiniLM-L6-v2"

        # Test batch embedding
        texts = ["First sentence.", "Second sentence.", "Third sentence."]
        batch_embeddings = embeddings.embed_batch(texts)

        assert isinstance(batch_embeddings, list)
        assert len(batch_embeddings) == 3
        assert all(len(emb) == 384 for emb in batch_embeddings)

    except ImportError:
        pytest.skip("sentence-transformers not installed")


def test_base_embeddings_interface():
    """Test that BaseEmbeddings defines the correct interface."""
    # Check abstract methods exist
    assert hasattr(BaseEmbeddings, 'embed')
    assert hasattr(BaseEmbeddings, 'embed_batch')
    assert hasattr(BaseEmbeddings, 'dimension')
    assert hasattr(BaseEmbeddings, 'model_name')

    # Test that BaseEmbeddings cannot be instantiated directly
    with pytest.raises(TypeError):
        BaseEmbeddings()


def test_openai_dimension_property():
    """Test OpenAI embedding dimension property."""
    small_model = OpenAIEmbeddings(api_key="fake", model="text-embedding-3-small")
    assert small_model.dimension == 1536

    large_model = OpenAIEmbeddings(api_key="fake", model="text-embedding-3-large")
    assert large_model.dimension == 3072


def test_voyage_dimension_property():
    """Test Voyage embedding dimension property."""
    try:
        voyage_3 = VoyageEmbeddings(api_key="fake", model="voyage-3")
        assert voyage_3.dimension == 1024

        voyage_lite = VoyageEmbeddings(api_key="fake", model="voyage-3-lite")
        assert voyage_lite.dimension == 512
    except ImportError:
        pytest.skip("voyageai not installed")
