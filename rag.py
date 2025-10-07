
"""Main RAG system implementation."""

import openai
import os
from typing import List, Dict
from .loaders import (
    WebLoader, 
    PDFLoader, 
    DocxLoader, 
    CSVLoader, 
    TxtLoader, 
    MarkdownLoader
)
from .chunkers import TextChunker
from .embeddings import OpenAIEmbeddings
from .storage import VectorStore


class RAGSystem:
    """Retrieval-Augmented Generation system."""
    
    def __init__(self, 
                 api_key: str = None,
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 embedding_model: str = "text-embedding-3-small",
                 llm_model: str = "gpt-4o-mini"):
        """
        Initialize RAG system.
        
        Args:
            api_key: OpenAI API key
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            embedding_model: OpenAI embedding model
            llm_model: OpenAI LLM model for generation
        """
        self.web_loader = WebLoader()
        self.pdf_loader = PDFLoader()
        self.docx_loader = DocxLoader()
        self.csv_loader = CSVLoader()
        self.txt_loader = TxtLoader()
        self.md_loader = MarkdownLoader()
        
        self.chunker = TextChunker(chunk_size, chunk_overlap)
        self.embeddings = OpenAIEmbeddings(api_key, embedding_model)
        self.vector_store = VectorStore()
        self.llm_model = llm_model
        self.client = openai.OpenAI(api_key=self.embeddings.api_key)
    
    def load_website(self, url: str) -> int:
        """
        Load content from a website.
        
        Args:
            url: Website URL
            
        Returns:
            Number of chunks added
        """
        print(f"Loading website: {url}")
        docs = self.web_loader.load(url)
        return self._process_documents(docs)
    
    def load_pdf(self, filepath: str) -> int:
        """
        Load content from a PDF file.
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            Number of chunks added
        """
        print(f"Loading PDF: {filepath}")
        docs = self.pdf_loader.load(filepath)
        return self._process_documents(docs)
    
    def load_docx(self, filepath: str) -> int:
        """
        Load content from a Word document.
        
        Args:
            filepath: Path to .docx file
            
        Returns:
            Number of chunks added
        """
        print(f"Loading Word document: {filepath}")
        docs = self.docx_loader.load(filepath)
        return self._process_documents(docs)
    
    def load_csv(self, filepath: str) -> int:
        """
        Load content from a CSV file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            Number of chunks added
        """
        print(f"Loading CSV: {filepath}")
        docs = self.csv_loader.load(filepath)
        return self._process_documents(docs)
    
    def load_txt(self, filepath: str) -> int:
        """
        Load content from a text file.
        
        Args:
            filepath: Path to text file
            
        Returns:
            Number of chunks added
        """
        print(f"Loading text file: {filepath}")
        docs = self.txt_loader.load(filepath)
        return self._process_documents(docs)
    
    def load_markdown(self, filepath: str) -> int:
        """
        Load content from a Markdown file.
        
        Args:
            filepath: Path to markdown file
            
        Returns:
            Number of chunks added
        """
        print(f"Loading Markdown: {filepath}")
        docs = self.md_loader.load(filepath)
        return self._process_documents(docs)
    
    def load_file(self, filepath: str) -> int:
        """
        Auto-detect file type and load content.
        
        Args:
            filepath: Path to file
            
        Returns:
            Number of chunks added
        """
        ext = os.path.splitext(filepath)[1].lower()
        
        loaders = {
            '.pdf': self.load_pdf,
            '.docx': self.load_docx,
            '.doc': self.load_docx,
            '.csv': self.load_csv,
            '.txt': self.load_txt,
            '.md': self.load_markdown,
            '.markdown': self.load_markdown
        }
        
        loader = loaders.get(ext)
        if loader:
            return loader(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _process_documents(self, documents: List[Dict]) -> int:
        """Process documents: chunk, embed, and store."""
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
        
        # Generate embeddings
        texts = [chunk['content'] for chunk in chunks]
        chunk_embeddings = self.embeddings.embed_batch(texts)
        
        # Store in vector store
        self.vector_store.add_documents(chunks, chunk_embeddings)
        
        print(f"Added {len(chunks)} chunks to vector store")
        return len(chunks)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant documents with scores
        """
        query_embedding = self.embeddings.embed(query)
        return self.vector_store.search(query_embedding, top_k)
    
    def query(self, question: str, top_k: int = 5, max_tokens: int = 500) -> str:
        """
        Query the RAG system and generate an answer.
        
        Args:
            question: Question to answer
            top_k: Number of context chunks to retrieve
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated answer
        """
        # Retrieve relevant context
        results = self.search(question, top_k)
        
        if not results:
            return "I don't have any relevant information to answer this question."
        
        # Build context
        context = "\n\n".join([
            f"[Source: {r['source']}]\n{r['content']}" 
            for r in results
        ])
        
        # Generate answer
        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer questions based on the provided context. If the context doesn't contain relevant information, say so. Cite sources when possible."
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
    
    def save(self, filepath: str):
        """Save RAG system to disk."""
        self.vector_store.save(filepath)
        print(f"RAG system saved to {filepath}")
    
    def load(self, filepath: str):
        """Load RAG system from disk."""
        self.vector_store.load(filepath)
        print(f"RAG system loaded from {filepath}")
    
    def get_stats(self) -> Dict:
        """Get system statistics."""
        return {
            'total_documents': len(self.vector_store),
            'chunk_size': self.chunker.chunk_size,
            'chunk_overlap': self.chunker.chunk_overlap,
            'embedding_model': self.embeddings.model,
            'llm_model': self.llm_model
        }

