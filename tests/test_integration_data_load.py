import os
import shutil
from pathlib import Path


def test_load_data_directory(tmp_path, monkeypatch):
    # Create a temporary data directory with a few simple files
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Create a small text file
    t1 = data_dir / "a.txt"
    t1.write_text("This is a test document.\n" * 10)

    # Create a small markdown file
    m1 = data_dir / "readme.md"
    m1.write_text("# Title\n\nSome content here.\n")

    # Run RAGSystem load
    from rag import RAGSystem

    rag = RAGSystem()
    summary = rag.load_file(str(data_dir), verbose=True)

    assert isinstance(summary, dict)
    assert summary["added_chunks"] > 0
    assert isinstance(summary["skipped_files"], list)
    assert isinstance(summary["errors"], list)
