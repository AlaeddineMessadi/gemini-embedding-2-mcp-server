# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
