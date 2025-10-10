# Knowledge Graph RAG Guide

## Overview

The RAGSystem now supports **Knowledge Graph** capabilities that work with **ANY embedding provider**! This combines the best of both worlds:

- 🔍 **Semantic Search**: Using embeddings (OpenAI, Voyage AI, or local models)
- 🕸️ **Structured Knowledge**: Graph relationships between entities
- 🎯 **Graph-Aware Retrieval**: Find information through relationships, not just similarity

## Key Insight

**Graph relationships are stored as metadata in ChromaDB**, while **embeddings are used for semantic search**. This means:

✅ You can use **any embedding provider** (local, Voyage, OpenAI)
✅ Graph structure is **independent of embeddings**
✅ You get **both semantic similarity AND structured relationships**

## Quick Start

### Basic Usage

```python
from ragsystem.graph_rag import GraphRAGSystem
from embeddings import SentenceTransformerEmbeddings

# Create with local embeddings (free!)
local_emb = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")

# Initialize Graph RAG
graph_rag = GraphRAGSystem(
    embeddings=local_emb,
    enable_graph_extraction=True,  # Enable graph extraction
    persist_directory="./graph_db"
)

# Load documents - automatically extracts entities and relationships
graph_rag.load_file("data/")

# Semantic search (uses embeddings)
results = graph_rag.search("What is Python?", top_k=5)

# Entity-based search (uses graph)
entity_results = graph_rag.search_by_entity("Python", top_k=5)

# Graph traversal
subgraph = graph_rag.traverse_from_entity("Python", max_hops=2)

# Query with graph context
answer = graph_rag.query(
    "How is Python related to machine learning?",
    use_graph_context=True  # Includes graph relationships in context
)
```

### With Different Embedding Providers

```python
from ragsystem.graph_rag import GraphRAGSystem
from embeddings import VoyageEmbeddings, OpenAIEmbeddings

# Option 1: Voyage AI + Knowledge Graph
voyage_emb = VoyageEmbeddings("voyage-3")
graph_rag = GraphRAGSystem(embeddings=voyage_emb)

# Option 2: OpenAI + Knowledge Graph
openai_emb = OpenAIEmbeddings("text-embedding-3-small")
graph_rag = GraphRAGSystem(embeddings=openai_emb)

# Option 3: Local (free!) + Knowledge Graph
from embeddings import SentenceTransformerEmbeddings
local_emb = SentenceTransformerEmbeddings("all-mpnet-base-v2")
graph_rag = GraphRAGSystem(embeddings=local_emb)
```

## Features

### 1. Automatic Entity Extraction

The system automatically extracts entities from your documents:

```python
# Get all entities in the graph
entities = graph_rag.get_entities()
# Returns: {'Python': 5, 'Machine Learning': 3, 'Guido van Rossum': 1, ...}

# Get statistics
stats = graph_rag.get_stats()
print(f"Total entities: {stats['total_entities']}")
print(f"Top entities: {stats['top_entities']}")
```

### 2. Relationship Extraction

Automatically identifies relationships between entities:

```python
# Get all relationships
relations = graph_rag.get_relations()
# Returns: [('Python', 'is_a', 'programming language'),
#           ('Python', 'created_by', 'Guido van Rossum'), ...]

stats = graph_rag.get_stats()
print(f"Total relations: {stats['total_relations']}")
```

### 3. Entity-Based Search

Find all chunks mentioning a specific entity:

```python
# Find all mentions of "Python"
results = graph_rag.search_by_entity("Python", top_k=10)

for result in results:
    print(f"Source: {result['source']}")
    print(f"Content: {result['content'][:100]}...")
    print(f"Entities: {result['graph']['entities']}")
    print(f"Relations: {result['graph']['relations']}")
```

### 4. Graph Traversal

Explore connected entities:

```python
# Find entities connected to "Python" within 2 hops
subgraph = graph_rag.traverse_from_entity("Python", max_hops=2)

print(f"Connected entities: {subgraph['entities']}")
print(f"Relationships:")
for source, relation, target in subgraph['relations']:
    print(f"  {source} --[{relation}]--> {target}")
```

### 5. Graph-Aware Queries

Use graph relationships to enhance LLM responses:

```python
# Query with graph context
answer = graph_rag.query(
    "How does Python relate to machine learning?",
    use_graph_context=True,  # Include graph relationships
    top_k=5
)

# The LLM receives:
# 1. Semantically similar chunks (from embeddings)
# 2. Relevant graph relationships (from metadata)
# This provides richer context for better answers!
```

## Visualization

### ASCII Art

```python
from ragsystem.knowledge_graph import GraphVisualizer

entities = graph_rag.get_entities()
relations = graph_rag.get_relations()

# Simple ASCII visualization
ascii_art = GraphVisualizer.to_ascii_art(entities, relations)
print(ascii_art)
```

### Mermaid Diagrams

```python
entity_list = list(entities.keys())[:20]
filtered_relations = [(s, r, t) for s, r, t in relations
                      if s in entity_list and t in entity_list]

mermaid = GraphVisualizer.to_mermaid(entity_list, filtered_relations)
print(mermaid)
# Copy output to https://mermaid.live for visualization
```

### Interactive HTML

```python
GraphVisualizer.save_html_visualization(
    entity_list,
    filtered_relations,
    "outputs/knowledge_graph.html"
)
# Open in browser for interactive D3.js visualization!
```

### Cytoscape.js Format

```python
# For programmatic use in web applications
cyto_data = GraphVisualizer.to_cytoscape(entity_list, filtered_relations)
# Use with Cytoscape.js library in your web app
```

## How It Works

### 1. Document Processing

```
Document → Chunks → Embeddings + Graph Extraction
                     ↓                    ↓
                Vector Search      Entity & Relation
                (Any provider!)      Extraction (LLM)
                     ↓                    ↓
                ChromaDB Storage (embeddings + graph metadata)
```

### 2. Storage Architecture

Each chunk in ChromaDB contains:

```json
{
  "id": "chunk_123",
  "embedding": [0.123, 0.456, ...],  // From ANY embedding provider
  "content": "Python is a programming language...",
  "metadata": {
    "source": "python.txt",
    "entities": ["Python", "programming language"],
    "entity_types": ["technology", "concept"],
    "relations": ["Python|is_a|programming language"],
    "keywords": ["python", "programming", "language"]
  }
}
```

### 3. Query Process

**Without Graph Context:**
1. Embed query using chosen embedding provider
2. Find similar chunks using vector search
3. Generate answer from retrieved chunks

**With Graph Context:**
1. Embed query using chosen embedding provider
2. Find similar chunks using vector search
3. Extract entities from retrieved chunks
4. **Find relationships involving those entities**
5. **Add graph relationships to context**
6. Generate answer with richer context

## Graph Extraction Methods

### LLM-Based Extraction (Default)

Uses GPT models to extract structured entities and relationships:

```python
graph_rag = GraphRAGSystem(
    enable_graph_extraction=True,  # Uses LLM
    llm_model="gpt-4o-mini"  # Model for extraction
)
```

**Pros:**
- High quality entity and relationship extraction
- Understands context and semantics
- Handles complex text

**Cons:**
- Requires API key and costs money
- Slower than pattern-based

### Pattern-Based Extraction (Fallback)

Uses regex patterns when LLM is unavailable:

```python
# Automatically falls back if no API key
graph_rag = GraphRAGSystem(
    api_key=None,  # No API key
    enable_graph_extraction=True
)
```

**Pros:**
- Free and fast
- No API required
- Works offline

**Cons:**
- Less accurate
- Misses complex relationships
- Simple entity detection

## Use Cases

### 1. Research & Literature Review

```python
# Load research papers
graph_rag.load_file("research_papers/")

# Find all papers mentioning a specific concept
results = graph_rag.search_by_entity("neural networks")

# Explore related concepts
subgraph = graph_rag.traverse_from_entity("neural networks", max_hops=3)
```

### 2. Technical Documentation

```python
# Load API documentation
graph_rag.load_file("docs/api/")

# Find relationships between classes/functions
entities = graph_rag.get_entities()
relations = graph_rag.get_relations()

# Query with context
answer = graph_rag.query(
    "How do I use the Database class?",
    use_graph_context=True
)
```

### 3. Legal/Compliance Documents

```python
# Use Voyage's legal-specific embeddings + graphs
from embeddings import VoyageEmbeddings

legal_emb = VoyageEmbeddings("voyage-law-2")
graph_rag = GraphRAGSystem(embeddings=legal_emb)

graph_rag.load_file("legal_docs/")

# Find all clauses referencing a specific entity
results = graph_rag.search_by_entity("intellectual property")
```

### 4. Knowledge Base Construction

```python
# Build a knowledge base from diverse sources
graph_rag.load_file("sources/")

# Export graph for visualization or analysis
entities = graph_rag.get_entities()
relations = graph_rag.get_relations()

# Save for external use
GraphVisualizer.save_html_visualization(
    list(entities.keys()),
    relations,
    "knowledge_base.html"
)
```

## Combining Multiple Embedding Providers

You can maintain separate collections with different embeddings while sharing the same knowledge graph structure:

```python
# Collection 1: Local embeddings
local_emb = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")
graph_local = GraphRAGSystem(
    embeddings=local_emb,
    collection_name="kb_local"
)
graph_local.load_file("data/")

# Collection 2: Voyage embeddings (same documents!)
voyage_emb = VoyageEmbeddings("voyage-3")
graph_voyage = GraphRAGSystem(
    embeddings=voyage_emb,
    collection_name="kb_voyage"
)
graph_voyage.load_file("data/")

# Both have the same graph structure but different retrieval!
# Compare results:
local_results = graph_local.search("query", top_k=5)
voyage_results = graph_voyage.search("query", top_k=5)
```

## Best Practices

### 1. Choose the Right Extraction Method

- **LLM-based**: For high-quality, production systems
- **Pattern-based**: For development, testing, or cost-sensitive applications

### 2. Optimize Chunk Size

```python
# Smaller chunks = more granular entities
graph_rag = GraphRAGSystem(
    chunk_size=500,   # Smaller for detailed extraction
    chunk_overlap=100
)

# Larger chunks = more context
graph_rag = GraphRAGSystem(
    chunk_size=1500,  # Larger for relationship context
    chunk_overlap=200
)
```

### 3. Use Graph Context Wisely

```python
# For factual queries: Use graph context
answer = graph_rag.query(
    "Who created Python?",
    use_graph_context=True  # Relationships help!
)

# For general queries: May not need graph
answer = graph_rag.query(
    "Explain machine learning",
    use_graph_context=False  # Semantic search sufficient
)
```

### 4. Visualize for Understanding

Always visualize your graph to understand:
- Entity coverage
- Relationship density
- Connection patterns

```python
entities = graph_rag.get_entities()
relations = graph_rag.get_relations()

print(GraphVisualizer.to_ascii_art(entities, relations))
GraphVisualizer.save_html_visualization(
    list(entities.keys())[:50],
    relations,
    "outputs/graph_check.html"
)
```

## Performance Considerations

### Embedding Provider Impact

| Provider | Speed | Cost | Graph Quality |
|----------|-------|------|---------------|
| Local (Sentence Transformers) | Medium | Free | Same* |
| Voyage AI | Fast | $$ | Same* |
| OpenAI | Fast | $ | Same* |

**Graph quality is determined by extraction method (LLM vs pattern), not embedding provider!*

### Extraction Performance

- **LLM extraction**: ~1-2 seconds per chunk (API latency)
- **Pattern extraction**: ~0.01 seconds per chunk (local regex)

### Storage Overhead

- Base chunk: ~1KB
- With graph metadata: ~2-3KB (50-100% overhead)
- Embeddings: 1.5-12KB depending on dimension

## Limitations

1. **Graph extraction quality depends on text quality**
   - Clear, well-structured text → Better graphs
   - Ambiguous or conversational text → Weaker graphs

2. **LLM extraction requires API key**
   - Pattern-based fallback is less accurate
   - Consider pre-processing for offline use

3. **Graph traversal is in-memory**
   - Large graphs (>10K entities) may be slow
   - Consider exporting to dedicated graph DB for massive scales

4. **Metadata size limits**
   - ChromaDB has metadata size limits
   - Very complex chunks may hit limits

## Examples

See [examples/knowledge_graph_demo.py](examples/knowledge_graph_demo.py) for complete working examples including:

1. **Graph + Local Embeddings** - Free, privacy-focused
2. **Graph + Voyage Embeddings** - High-quality retrieval
3. **Visualization** - Multiple output formats
4. **Comparison** - Different embedding providers

Run the demo:
```bash
uv run python examples/knowledge_graph_demo.py
```

## API Reference

### GraphRAGSystem

```python
graph_rag = GraphRAGSystem(
    embeddings=None,              # Custom embedding provider
    enable_graph_extraction=True,  # Enable graph features
    llm_model="gpt-4o-mini",      # Model for extraction
    chunk_size=1000,              # Chunk size
    chunk_overlap=200,            # Chunk overlap
    persist_directory="./db",     # Storage directory
    collection_name="graph_docs"  # Collection name
)
```

#### Methods

- `load_file(filepath)` - Load documents with graph extraction
- `search(query, top_k)` - Semantic search using embeddings
- `search_by_entity(entity, top_k)` - Find chunks with entity
- `get_entities()` - Get all entities and counts
- `get_relations()` - Get all relationships
- `traverse_from_entity(entity, max_hops)` - Graph traversal
- `query(question, use_graph_context)` - LLM query with optional graph
- `get_stats()` - System and graph statistics

### GraphVisualizer

```python
from ragsystem.knowledge_graph import GraphVisualizer

# ASCII art
GraphVisualizer.to_ascii_art(entities, relations)

# Mermaid diagram
GraphVisualizer.to_mermaid(entity_list, relations)

# Interactive HTML
GraphVisualizer.save_html_visualization(entities, relations, "output.html")

# Cytoscape.js format
GraphVisualizer.to_cytoscape(entity_list, relations)
```

## Summary

✨ **Knowledge graphs enhance RAG with structured relationships**
🔧 **Works with ANY embedding provider** (local, Voyage, OpenAI)
📊 **Multiple visualization options**
🎯 **Graph-aware retrieval for better context**
🆓 **Can run completely free with local embeddings + pattern extraction**

The combination of semantic search (embeddings) and structured knowledge (graphs) provides the best of both worlds for intelligent information retrieval!
