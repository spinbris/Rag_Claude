"""Graph-enhanced RAG system."""

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

import openai
import os
from typing import List, Dict, Optional
from .chunkers import TextChunker
from .embeddings import OpenAIEmbeddings
from .knowledge_graph import KnowledgeGraphExtractor, GraphEnhancedStorage


class GraphRAGSystem:
    """
    RAG system with knowledge graph capabilities.

    Works with ANY embedding provider - embeddings are used for semantic search,
    while graph structure is stored as metadata.
    """

    def __init__(
        self,
        api_key: str = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_model: str = "text-embedding-3-small",
        llm_model: str = "gpt-4o-mini",
        persist_directory: str = "./chroma_graph_db",
        collection_name: str = "graph_rag_documents",
        embeddings: Optional[object] = None,
        enable_graph_extraction: bool = True
    ):
        """
        Initialize Graph RAG system.

        Args:
            api_key: OpenAI API key (for LLM and default embeddings)
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            embedding_model: Embedding model (ignored if embeddings provided)
            llm_model: LLM model for generation
            persist_directory: Directory for ChromaDB persistence
            collection_name: Name of ChromaDB collection
            embeddings: Custom embedding provider (works with ANY provider!)
            enable_graph_extraction: Whether to extract graph relationships
        """
        # Import loaders lazily
        from loaders import BaseLoader

        def _try_import_loader(loader_name):
            try:
                from loaders import __getattr__ as loader_getattr
                return loader_getattr(loader_name)
            except (ImportError, ModuleNotFoundError):
                return None

        WebLoader = _try_import_loader("WebLoader")
        PDFLoader = _try_import_loader("PDFLoader")
        DocxLoader = _try_import_loader("DocxLoader")
        CSVLoader = _try_import_loader("CSVLoader")
        TxtLoader = _try_import_loader("TxtLoader")
        MarkdownLoader = _try_import_loader("MarkdownLoader")

        self.web_loader = WebLoader() if WebLoader is not None else None
        self.pdf_loader = PDFLoader() if PDFLoader is not None else None
        self.docx_loader = DocxLoader() if DocxLoader is not None else None
        self.csv_loader = CSVLoader() if CSVLoader is not None else None
        self.txt_loader = TxtLoader() if TxtLoader is not None else None
        self.md_loader = MarkdownLoader() if MarkdownLoader is not None else None

        self.chunker = TextChunker(chunk_size, chunk_overlap)

        # Use provided embeddings or create default OpenAI embeddings
        if embeddings is not None:
            self.embeddings = embeddings
        else:
            self.embeddings = OpenAIEmbeddings(api_key, embedding_model)

        # Graph-enhanced storage
        self.vector_store = GraphEnhancedStorage(persist_directory, collection_name)

        # Knowledge graph extractor
        self.enable_graph_extraction = enable_graph_extraction
        if enable_graph_extraction:
            llm_api_key = api_key
            if isinstance(self.embeddings, OpenAIEmbeddings) and self.embeddings.api_key:
                llm_api_key = self.embeddings.api_key
            self.graph_extractor = KnowledgeGraphExtractor(llm_api_key, llm_model)
        else:
            self.graph_extractor = None

        # LLM for generation
        self.llm_model = llm_model
        llm_api_key = api_key
        if isinstance(self.embeddings, OpenAIEmbeddings) and self.embeddings.api_key:
            llm_api_key = self.embeddings.api_key
        self.client = openai.OpenAI(api_key=llm_api_key)

    def _process_documents(self, documents: List[Dict]) -> int:
        """Process documents with graph extraction."""
        chunks = []

        for doc in documents:
            text_chunks = self.chunker.chunk(doc['content'])

            for chunk in text_chunks:
                chunks.append({
                    'content': chunk,
                    'source': doc['source'],
                    'type': doc['type']
                })

        if not chunks:
            print("No chunks created")
            return 0

        print(f"Created {len(chunks)} chunks, generating embeddings...")

        # Generate embeddings (works with ANY embedding provider!)
        texts = [chunk['content'] for chunk in chunks]
        chunk_embeddings = self.embeddings.embed_batch(texts)

        # Extract graph metadata if enabled
        graph_metadata = None
        if self.enable_graph_extraction and self.graph_extractor:
            print(f"Extracting knowledge graph relationships...")
            graph_metadata = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"chunk_{i}"
                metadata = self.graph_extractor.build_graph_metadata(chunk['content'], chunk_id)
                graph_metadata.append(metadata)
            print(f"Extracted graph data from {sum(1 for m in graph_metadata if m.get('has_graph_data'))} chunks")

        # Add to graph-enhanced storage
        self.vector_store.add_documents_with_graph(chunks, chunk_embeddings, graph_metadata)

        print(f"Added {len(chunks)} chunks to graph-enhanced vector store")
        return len(chunks)

    def load_file(self, filepath: str, verbose: bool = False):
        """Load file with graph extraction."""
        # Reuse the same logic from RAGSystem
        import os

        if os.path.isdir(filepath):
            total = 0
            skipped = []
            errors = []

            for root, _, files in os.walk(filepath):
                for fname in files:
                    full = os.path.join(root, fname)
                    try:
                        added = self.load_file(full, verbose=False)
                        if isinstance(added, dict):
                            added = added.get('added_chunks', 0)
                        total += added
                    except ValueError:
                        skipped.append(full)
                    except Exception as e:
                        errors.append({'file': full, 'error': str(e)})

            if verbose:
                return {
                    'added_chunks': total,
                    'skipped_files': skipped,
                    'errors': errors,
                }
            return total

        # Single file processing
        ext = os.path.splitext(filepath)[1].lower()

        loaders = {
            '.pdf': self.pdf_loader,
            '.docx': self.docx_loader,
            '.doc': self.docx_loader,
            '.csv': self.csv_loader,
            '.txt': self.txt_loader,
            '.md': self.md_loader,
            '.markdown': self.md_loader,
        }

        loader = loaders.get(ext)
        if loader and hasattr(loader, 'load'):
            print(f"Loading {filepath}...")
            docs = loader.load(filepath)
            return self._process_documents(docs)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Semantic search with graph metadata."""
        query_embedding = self.embeddings.embed(query)
        return self.vector_store.search(query_embedding, top_k)

    def search_by_entity(self, entity: str, top_k: int = 10) -> List[Dict]:
        """Find chunks containing a specific entity."""
        return self.vector_store.find_by_entity(entity, top_k)

    def get_entities(self) -> Dict[str, int]:
        """Get all entities in the knowledge graph."""
        return self.vector_store.get_all_entities()

    def get_relations(self) -> List[tuple]:
        """Get all relationships in the knowledge graph."""
        return self.vector_store.get_all_relations()

    def traverse_from_entity(self, entity: str, max_hops: int = 2) -> Dict:
        """Traverse the graph starting from an entity."""
        return self.vector_store.traverse_graph(entity, max_hops)

    def query(self, question: str, top_k: int = 5, use_graph_context: bool = True, max_tokens: int = 500) -> str:
        """
        Answer question using RAG with optional graph context.

        Args:
            question: User question
            top_k: Number of relevant chunks to retrieve
            use_graph_context: Whether to include graph relationships in context
            max_tokens: Maximum tokens in response

        Returns:
            Generated answer
        """
        results = self.search(question, top_k)

        if not results:
            return "I don't have any relevant information to answer this question."

        # Build context
        context_parts = []
        entities_mentioned = set()

        for r in results:
            context_parts.append(f"[Source: {r['source']}]\n{r['content']}")

            # Collect entities if graph context is enabled
            if use_graph_context and 'graph' in r:
                entities_mentioned.update(r['graph']['entities'])

        context = "\n\n".join(context_parts)

        # Add graph context if available
        if use_graph_context and entities_mentioned:
            # Get relationships involving mentioned entities
            all_relations = self.get_relations()
            relevant_relations = [
                (s, r, t) for s, r, t in all_relations
                if s in entities_mentioned or t in entities_mentioned
            ]

            if relevant_relations:
                graph_context = "\n\nKnowledge Graph Relationships:\n"
                for s, r, t in relevant_relations[:10]:  # Limit to avoid context overflow
                    graph_context += f"- {s} {r} {t}\n"
                context += graph_context

        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant with access to a knowledge graph. Answer questions based on the provided context and relationships. Cite sources when possible."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
                }
            ],
            temperature=0.7,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    def get_stats(self) -> Dict:
        """Get system statistics including graph info."""
        entities = self.get_entities()
        relations = self.get_relations()

        return {
            'total_documents': len(self.vector_store),
            'chunk_size': self.chunker.chunk_size,
            'chunk_overlap': self.chunker.chunk_overlap,
            'embedding_model': self.embeddings.model_name,
            'embedding_dimension': self.embeddings.dimension,
            'llm_model': self.llm_model,
            'graph_enabled': self.enable_graph_extraction,
            'total_entities': len(entities),
            'total_relations': len(relations),
            'top_entities': sorted(entities.items(), key=lambda x: x[1], reverse=True)[:10]
        }
