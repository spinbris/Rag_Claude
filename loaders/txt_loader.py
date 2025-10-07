"""Plain text file loader."""

from typing import List, Dict
from .base import BaseLoader


class TxtLoader(BaseLoader):
    """Load content from plain text files."""
    
    def __init__(self, encoding: str = 'utf-8'):
        """
        Initialize text loader.
        
        Args:
            encoding: Text file encoding
        """
        self.encoding = encoding
    
    def load(self, filepath: str) -> List[Dict[str, str]]:
        """
        Load text from a plain text file.
        
        Args:
            filepath: Path to text file
            
        Returns:
            List containing a single document dictionary
        """
        try:
            with open(filepath, 'r', encoding=self.encoding) as f:
                text = f.read()
            
            if not text.strip():
                raise ValueError("Text file is empty")
            
            return [{
                'content': text,
                'source': filepath,
                'type': 'txt'
            }]
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    text = f.read()
                return [{
                    'content': text,
                    'source': filepath,
                    'type': 'txt'
                }]
            except Exception as e:
                raise ValueError(f"Error loading text file {filepath}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading text file {filepath}: {str(e)}")


