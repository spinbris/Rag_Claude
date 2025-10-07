
"""Base class for document loaders."""

from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLoader(ABC):
    """Abstract base class for document loaders."""
    
    @abstractmethod
    def load(self, source: str) -> List[Dict[str, str]]:
        """
        Load documents from a source.
        
        Args:
            source: Path or URL to the source
            
        Returns:
            List of document dictionaries with 'content', 'source', and 'type'
        """
        pass
