"""PDF document loader."""

from pypdf import PdfReader
from typing import List, Dict
from .base import BaseLoader


class PDFLoader(BaseLoader):
    def load(self, filepath: str) -> List[Dict[str, str]]:
        try:
            reader = PdfReader(filepath)
            text = ""

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            if not text.strip():
                raise ValueError("No text could be extracted from PDF")

            return [{
                'content': text,
                'source': filepath,
                'type': 'pdf'
            }]
        except Exception as e:
            raise ValueError(f"Error loading PDF {filepath}: {str(e)}")
