
"""Text chunking with overlap."""

from typing import List


class TextChunker:
    """Split text into overlapping chunks."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize text chunker.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                last_question = chunk.rfind('?')
                last_exclamation = chunk.rfind('!')
                
                break_point = max(last_period, last_newline, 
                                 last_question, last_exclamation)
                
                # Only break if we found a reasonable boundary
                if break_point > self.chunk_size * 0.5:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunk = chunk.strip()
            if len(chunk) > 50:  # Minimum chunk size
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
        
        return chunks