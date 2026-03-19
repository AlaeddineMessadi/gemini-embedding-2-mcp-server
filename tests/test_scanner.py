import pytest
from pathlib import Path
from gemini_mcp.parsers.scanner import scan_directory, chunk_text

def test_chunk_text():
    # 2500 character string
    text = "A" * 2500
    
    # Chunk with 1000 size and 200 overlap
    chunks = chunk_text(text, chunk_size=1000, overlap=200)
    
    assert len(chunks) == 4 
    assert len(chunks[0]) == 1000
    assert len(chunks[3]) == 100

def test_scan_directory_junk_filter(tmp_path):
    # Create test directory structure
    (tmp_path / "valid.txt").write_text("Hello World!")
    
    # 1. Test Node Modules ignores native 
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "junk.txt").write_text("Ignore me")
    
    # 2. Test dynamic custom ignore
    (tmp_path / "secret.env").write_text("API_KEY=123")
    
    # 3. Test hidden file skip
    (tmp_path / ".hidden.txt").write_text("Invisible")
    
    # Need to convert generator to list
    documents = list(scan_directory(str(tmp_path), ignore=["*.env"]))
    
    paths = [doc["metadata"]["source"] for doc in documents]
    
    # Should include valid.txt
    assert any("valid.txt" in p for p in paths)
    
    # Should skip node_modules
    assert not any("node_modules" in p for p in paths)
    
    # Should skip custom ignore "*.env"
    assert not any("secret.env" in p for p in paths)
    
    # Should skip hidden
    assert not any(".hidden" in p for p in paths)

def test_scan_directory_root_safety():
    # Calling on root should return an empty generator softly, handled by logger without catastrophic raising in scanner.py
    # As per scanner.py, it returns early if abs_path is root.
    documents = list(scan_directory("/"))
    assert len(documents) == 0
