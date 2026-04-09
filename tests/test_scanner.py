from gemini_mcp.parsers.scanner import (
    scan_directory,
    chunk_text,
    preview_directory_scan,
)


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


def test_scan_directory_adds_rich_metadata(tmp_path):
    file_path = tmp_path / "notes.md"
    file_path.write_text("Hello multimodal world")

    documents = list(scan_directory(str(tmp_path)))

    assert len(documents) == 1
    metadata = documents[0]["metadata"]
    assert metadata["filename"] == "notes.md"
    assert metadata["extension"] == ".md"
    assert metadata["directory_root"] == str(tmp_path)
    assert metadata["modality"] == "text"
    assert metadata["page_number"] is None
    assert metadata["size_bytes"] > 0
    assert metadata["mtime"] > 0


def test_preview_directory_scan_summarizes_modalities_and_skips(tmp_path):
    (tmp_path / "notes.md").write_text("Hello world")
    (tmp_path / "poster.png").write_bytes(b"fake-png")
    (tmp_path / ".hidden.txt").write_text("hidden")
    (tmp_path / "secret.env").write_text("TOKEN=123")

    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "junk.txt").write_text("ignore me")

    preview = preview_directory_scan(str(tmp_path), ignore=["*.env"])

    assert preview["eligible_files"] == 2
    assert preview["modality_counts"]["text"] == 1
    assert preview["modality_counts"]["image"] == 1
    assert preview["skip_reasons"]["hidden"] == 1
    assert preview["skip_reasons"]["custom_ignore"] == 1
    assert preview["skip_reasons"]["ignored_directory"] == 1
