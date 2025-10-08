"""Text chunking with overlap."""

from typing import List


class TextChunker:
    """Split text into overlapping chunks."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]

            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                last_question = chunk.rfind('?')
                last_exclamation = chunk.rfind('!')

                break_point = max(last_period, last_newline, last_question, last_exclamation)

                if break_point > self.chunk_size * 0.5:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1

            chunk = chunk.strip()
            if len(chunk) > 50:
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks
