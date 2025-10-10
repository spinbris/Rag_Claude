# Custom Embeddings Guide

The RAGSystem now supports multiple embedding providers, giving you flexibility to choose the best option for your use case.

## Available Embedding Providers

### 1. **Local Embeddings (Sentence Transformers)** 🆓
- **Pros**: Free, privacy-focused, runs offline, no API costs
- **Cons**: Requires more compute resources, slower than API-based
- **Best for**: Privacy-sensitive applications, cost optimization, offline usage

### 2. **Voyage AI Embeddings** 🚀
- **Pros**: High-quality, optimized for retrieval, domain-specific models
- **Cons**: Requires API key, usage costs
- **Best for**: Production applications requiring best-in-class retrieval quality

### 3. **OpenAI Embeddings** (Default) ✨
- **Pros**: Good general purpose, easy to use, well-documented
- **Cons**: Requires API key, usage costs
- **Best for**: General RAG applications, getting started quickly

## Quick Start

### Using Local Embeddings (Free!)

```python
from ragsystem import RAGSystem
from embeddings import SentenceTransformerEmbeddings

# Create local embeddings
local_embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2",  # 384 dimensions, fast
    device="cpu"  # or "cuda" for GPU
)

# Initialize RAG with local embeddings
rag = RAGSystem(
    embeddings=local_embeddings,
    persist_directory="./chroma_db_local"
)

# Load and query
rag.load_file("data/")
answer = rag.query("What is this about?")
```

### Using Voyage AI Embeddings

```python
from ragsystem import RAGSystem
from embeddings import VoyageEmbeddings

# Create Voyage embeddings (uses VOYAGE_API_KEY from .env)
voyage_embeddings = VoyageEmbeddings(
    model="voyage-3"  # 1024 dimensions
)

# Initialize RAG
rag = RAGSystem(
    embeddings=voyage_embeddings,
    persist_directory="./chroma_db_voyage"
)

rag.load_file("data/")
answer = rag.query("What is this about?")
```

### Using OpenAI Embeddings (Default)

```python
from ragsystem import RAGSystem

# Method 1: Use default (implicitly creates OpenAI embeddings)
rag = RAGSystem(
    embedding_model="text-embedding-3-small",
    persist_directory="./chroma_db"
)

# Method 2: Explicit creation
from embeddings import OpenAIEmbeddings

openai_embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)
rag = RAGSystem(embeddings=openai_embeddings)
```

## Available Models

### Sentence Transformers (Local)

| Model | Dimensions | Speed | Quality | Use Case |
|-------|------------|-------|---------|----------|
| `all-MiniLM-L6-v2` | 384 | ⚡️⚡️⚡️ | ⭐️⭐️⭐️ | Fast, general purpose |
| `all-mpnet-base-v2` | 768 | ⚡️⚡️ | ⭐️⭐️⭐️⭐️ | Better quality |
| `multi-qa-mpnet-base-dot-v1` | 768 | ⚡️⚡️ | ⭐️⭐️⭐️⭐️ | Optimized for Q&A |

### Voyage AI

| Model | Dimensions | Use Case |
|-------|------------|----------|
| `voyage-3` | 1024 | Latest general-purpose |
| `voyage-3-lite` | 512 | Faster, cost-effective |
| `voyage-code-3` | 1024 | Optimized for code |
| `voyage-finance-2` | 1024 | Domain-specific: Finance |
| `voyage-law-2` | 1024 | Domain-specific: Legal |

### OpenAI

| Model | Dimensions | Use Case |
|-------|------------|----------|
| `text-embedding-3-small` | 1536 | General purpose, cost-effective |
| `text-embedding-3-large` | 3072 | Highest quality |

## Environment Setup

### For Local Embeddings
No API key needed! Just ensure dependencies are installed:
```bash
uv sync
```

### For Voyage AI
Add to your `.env` file:
```bash
VOYAGE_API_KEY=your_voyage_api_key
```

### For OpenAI
Add to your `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key
```

## Examples

See [examples/custom_embeddings.py](examples/custom_embeddings.py) for complete working examples including:
- Local embeddings usage
- Voyage AI embeddings usage
- OpenAI embeddings usage
- Comparing different providers

Run the examples:
```bash
python examples/custom_embeddings.py
```

## Advanced Usage

### Creating a Custom Embedding Provider

You can create your own embedding provider by extending the `BaseEmbeddings` class:

```python
from embeddings import BaseEmbeddings
from typing import List

class MyCustomEmbeddings(BaseEmbeddings):
    def embed(self, text: str) -> List[float]:
        # Your embedding logic here
        pass

    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        # Your batch embedding logic here
        pass

    @property
    def dimension(self) -> int:
        return 768  # Your embedding dimension

    @property
    def model_name(self) -> str:
        return "my-custom-model"
```

Then use it with RAGSystem:
```python
my_embeddings = MyCustomEmbeddings()
rag = RAGSystem(embeddings=my_embeddings)
```

## Performance Considerations

### Local Embeddings
- **CPU**: ~50-200 texts/second (depends on model size)
- **GPU**: ~500-2000 texts/second
- **Memory**: 100-500MB (model weights)

### API-based Embeddings
- **Throughput**: Limited by API rate limits
- **Latency**: Network dependent (~100-500ms per batch)
- **Cost**: Per-token pricing

## Best Practices

1. **For Development**: Use local embeddings (free, fast iterations)
2. **For Production**: Use Voyage or OpenAI (better quality, managed infrastructure)
3. **For Privacy**: Use local embeddings (data never leaves your machine)
4. **For Code RAG**: Use `voyage-code-3` or local code-specific models
5. **For Domain-Specific**: Use Voyage's domain models (finance, law, etc.)

## Troubleshooting

### Local embeddings not working?
```bash
uv add sentence-transformers
```

### Voyage embeddings failing?
- Check your `.env` file has `VOYAGE_API_KEY`
- Verify API key is valid at https://www.voyageai.com

### Different embeddings = Different collections
⚠️ **Important**: You cannot mix embedding providers in the same ChromaDB collection. Each embedding provider should use a separate collection or database.

```python
# ✅ Good: Separate collections
local_rag = RAGSystem(embeddings=local_emb, collection_name="local_docs")
voyage_rag = RAGSystem(embeddings=voyage_emb, collection_name="voyage_docs")

# ❌ Bad: Same collection, different embeddings
# This will cause dimension mismatch errors!
```

## Migration Guide

### From OpenAI to Local Embeddings

```python
# Old code
rag = RAGSystem(
    embedding_model="text-embedding-3-small",
    persist_directory="./chroma_db"
)

# New code (local embeddings)
from embeddings import SentenceTransformerEmbeddings

local_emb = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")
rag = RAGSystem(
    embeddings=local_emb,
    persist_directory="./chroma_db_local",  # Use different directory!
    collection_name="local_docs"  # Use different collection!
)

# Re-index your documents
rag.load_file("data/")
```

## Cost Comparison

| Provider | Cost per 1M tokens | 1000 docs (~500K tokens) |
|----------|-------------------|--------------------------|
| Local (Sentence Transformers) | $0 | $0 |
| Voyage AI | ~$0.12 | ~$0.06 |
| OpenAI (3-small) | ~$0.02 | ~$0.01 |
| OpenAI (3-large) | ~$0.13 | ~$0.065 |

*Prices are approximate and subject to change*

## Summary

Choose your embedding provider based on your needs:

- 💰 **Save money**: Local embeddings
- 🔒 **Privacy first**: Local embeddings
- 🎯 **Best quality**: Voyage AI or OpenAI 3-large
- ⚡️ **Fast start**: OpenAI 3-small (default)
- 📚 **Domain-specific**: Voyage domain models
