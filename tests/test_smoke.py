import pytest
from chunkers.text_chunker import TextChunker
from storage.vector_storage import VectorStore


@pytest.fixture
def chunker() -> TextChunker:
    return TextChunker(chunk_size=1000, chunk_overlap=200)


@pytest.fixture
def vector_store() -> VectorStore:
    return VectorStore()


def test_chunker_basic(chunker: TextChunker):
    text = "This is a sentence. " * 40
    chunks = chunker.chunk(text)
    # There should be at least one chunk and no chunk shorter than 50 chars
    assert isinstance(chunks, list)
    assert len(chunks) >= 1
    assert all(len(c) >= 50 for c in chunks)


def test_vector_store_add_and_search(vector_store: VectorStore):
    # Create three simple documents and deterministic embeddings
    docs = [
        {"content": "apple orange banana", "source": "a", "type": "text"},
        {"content": "car bus train", "source": "b", "type": "text"},
        {"content": "python java c++", "source": "c", "type": "text"},
    ]

    # Simple deterministic embeddings (dim=4)
    embs = [[i + j for j in range(4)] for i in range(len(docs))]

    vector_store.add_documents(docs, embs)

    # Searching with the first embedding should return the first document as top result
    results = vector_store.search(embs[0], top_k=1)
    assert len(results) == 1
    assert results[0]["source"] == "a"


def test_rag_instantiation_and_mock_embeddings(monkeypatch):
    # Import here to avoid side-effects at module import time
    from rag import RAGSystem
    from embeddings.openai_embeddings import OpenAIEmbeddings

    # Provide a fake client that returns predictable embeddings
    class FakeClient:
        class embeddings:
            @staticmethod
            def create(input, model=None):
                # emulate response object shape expected by code
                class Item:
                    def __init__(self, embedding):
                        self.embedding = embedding

                class Resp:
                    def __init__(self, data):
                        self.data = data

                data = [Item([0.1] * 8) for _ in (input if isinstance(input, list) else [input])]
                return Resp(data)

    # Monkeypatch the OpenAIEmbeddings to use the fake client when _ensure_client is called
    def fake_ensure(self):
        self.client = FakeClient()

    monkeypatch.setattr(OpenAIEmbeddings, "_ensure_client", fake_ensure)

    # Now instantiate RAGSystem and perform a small pipeline run that calls embeddings
    rs = RAGSystem(api_key="fake")
    # Add a small document and ensure save/load or search doesn't blow up
    docs = [{"content": "hello world", "source": "test", "type": "text"}]
    chunks = rs.chunker.chunk(docs[0]["content"])
    assert isinstance(chunks, list)

    # Generate embeddings via OpenAIEmbeddings and add to vector store
    embs = rs.embeddings.embed_batch(chunks)
    rs.vector_store.add_documents([{"content": c, "source": "test", "type": "text"} for c in chunks], embs)

    # Basic search
    q_emb = rs.embeddings.embed(chunks[0])
    results = rs.vector_store.search(q_emb, top_k=1)
    assert isinstance(results, list)
    if results:
        assert "score" in results[0]
