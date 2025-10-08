"""Base class for document loaders."""

from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLoader(ABC):
    @abstractmethod
    def load(self, source: str) -> List[Dict[str, str]]:
        pass
