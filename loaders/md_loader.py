
"""Markdown file loader."""

from typing import List, Dict
from .base import BaseLoader


class MarkdownLoader(BaseLoader):
    """Load content from Markdown files."""
    
    def __init__(self, encoding: str = 'utf-8', strip_markdown: bool = False):
        """
        Initialize markdown loader.
        
        Args:
            encoding: Text file encoding
            strip_markdown: If True, remove markdown formatting
        """
        self.encoding = encoding
        self.strip_markdown = strip_markdown
    
    def load(self, filepath: str) -> List[Dict[str, str]]:
        """
        Load text from a Markdown file.
        
        Args:
            filepath: Path to markdown file
            
        Returns:
            List containing a single document dictionary
        """
        try:
            with open(filepath, 'r', encoding=self.encoding) as f:
                text = f.read()
            
            if not text.strip():
                raise ValueError("Markdown file is empty")
            
            if self.strip_markdown:
                # Basic markdown stripping (you could use a library like markdown for better parsing)
                import re
                # Remove headers
                text = re.sub(r'#{1,6}\s+', '', text)
                # Remove bold/italic
                text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
                text = re.sub(r'\*([^\*]+)\*', r'\1', text)
                text = re.sub(r'__([^_]+)__', r'\1', text)
                text = re.sub(r'_([^_]+)_', r'\1', text)
                # Remove links but keep text
                text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
                # Remove inline code
                text = re.sub(r'`([^`]+)`', r'\1', text)
                # Remove code blocks
                text = re.sub(r'```[^`]*```', '', text)
            
            return [{
                'content': text,
                'source': filepath,
                'type': 'markdown'
            }]
            
        except Exception as e:
            raise ValueError(f"Error loading markdown file {filepath}: {str(e)}")