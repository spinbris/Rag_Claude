"""ragsystem package - exposes RAGSystem lazily to avoid heavy imports.

Importing this package will not import all submodules (which may pull in
optional dependencies like `requests` or `pypdf`). Accessing `RAGSystem`
will import `ragsystem.rag` on demand.
"""
try:
	from dotenv import load_dotenv

	load_dotenv(override=True)
except Exception:
	pass

__all__ = ["RAGSystem"]

def __getattr__(name: str):
	if name == "RAGSystem":
		import importlib

		mod = importlib.import_module("ragsystem.rag")
		return getattr(mod, "RAGSystem")
	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
	return __all__
