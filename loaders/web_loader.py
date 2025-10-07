
"""Web page loader."""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from .base import BaseLoader


class WebLoader(BaseLoader):
    """Load content from web pages."""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize web loader.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    def load(self, url: str) -> List[Dict[str, str]]:
        """
        Load and extract text from a web page.
        
        Args:
            url: Web page URL
            
        Returns:
            List containing a single document dictionary
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = ' '.join(text.split())
            
            return [{
                'content': text,
                'source': url,
                'type': 'website'
            }]
            
        except Exception as e:
            raise ValueError(f"Error loading website {url}: {str(e)}")
