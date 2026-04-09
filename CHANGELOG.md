# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2026-04-10

### Changed
- **Python Support Alignment**: Raised the documented and declared Python support floor to `3.11+` to match the current dependency graph.
- **CI Matrix Fix**: Updated CI to test supported Python versions instead of failing on unsupported `3.10`.
- **Stable Install Docs**: Reworked README install guidance to use a release-tag placeholder instead of hard-coding a single version in perpetuity.

## [1.2.0] - 2026-04-10

### Added
- **Preview Before Indexing**: Added `preview_directory()` so agents and users can inspect what will be indexed, broken down by modality and skip reason, before spending time or tokens.
- **Result Context Retrieval**: Added `get_result_context()` to pull exact chunk or page-adjacent context from previously indexed files.
- **Richer Metadata Model**: Indexed entries now store filename, extension, modality, directory root, page number, file size, and modification time for stronger downstream retrieval and inspection.
- **Use Case and Result Model Docs**: Added dedicated documentation explaining practical workflows and the server's result metadata.

### Changed
- **Search Precision**: `search_my_documents()` now supports compact retrieval filters for scope, type, path prefix, extension, and modality.
- **Directory Listing Semantics**: `list_indexed_directories()` now returns indexed parent directories instead of raw file paths.
- **Product Positioning**: Reworked the README and technical docs to describe the server as a multimodal local memory engine rather than a generic local RAG utility.

## [1.1.1] - 2026-04-10

### Added
- **Docker Packaging**: Added a root `Dockerfile` and `.dockerignore` so the server can be built and validated by MCP registries such as Glama.

### Changed
- **Package Version Alignment**: Bumped the project version to `1.1.1` so the packaged metadata no longer lags behind the published release history.

## [1.1.0] - 2024-XX-XX

### Added
- **Smart Deduplication & Token Saver**: The server now pre-calculates MD5 hashes of local files before querying the Gemini API. If the file is unmodified, it bypasses the embedding pipeline entirely.
- **Ghost Pruning**: The server now actively deletes the old vectors from ChromaDB when a file modification is detected.
- **One-Click Deployment**: Added `smithery.yaml` to officially support 1-click installation via the Smithery CLI.

### Changed
- **Explicit Citations**: Search results now explicitly print out the `File Name` and the absolute `File Path` so clients using this MCP Server immediately show rich file context.

## [1.0.0] - 2024-XX-XX

### Added
- **Initial Release**: Core MCP Server functionality using `gemini-embedding-2-preview`.
- **Ultimate Multimodality**: Native ingestion and vector embedding of Images (`.jpg`, `.webp`), Video (`.mp4`), and Audio (`.mp3`, `.wav`) using `types.Part.from_bytes`.
- **Visual PDF RAG**: PyMuPDF integration to parse PDFs page-by-page as HD PNG images for visual layout, chart, and plot embedding.
- **Agent Guardrails**: Memory exhaustion prevention, junk filtering, wildcard blacklisting, and API exponential backoff.
- **Tools Included**: `index_directory`, `search_my_documents`, `list_indexed_directories`, `sync_indexed_directories`, `remove_directory_from_index`, `gemini://database-stats`.
