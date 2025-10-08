
"""Document loaders for various sources."""

from .base import BaseLoader

# Lazy imports to handle optional dependencies
def __getattr__(name):
    if name == "WebLoader":
        from .web_loader import WebLoader
        return WebLoader
    elif name == "PDFLoader":
        from .pdf_loader import PDFLoader
        return PDFLoader
    elif name == "DocxLoader":
        from .docx_loader import DocxLoader
        return DocxLoader
    elif name == "CSVLoader":
        from .csv_loader import CSVLoader
        return CSVLoader
    elif name == "TxtLoader":
        from .txt_loader import TxtLoader
        return TxtLoader
    elif name == "MarkdownLoader":
        from .md_loader import MarkdownLoader
        return MarkdownLoader
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "BaseLoader",
    "WebLoader",
    "PDFLoader",
    "DocxLoader",
    "CSVLoader",
    "TxtLoader",
    "MarkdownLoader"
]