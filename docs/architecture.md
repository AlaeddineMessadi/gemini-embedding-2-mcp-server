# Architecture

`gemini-embedding-2-mcp-server` is a local-first multimodal memory layer for AI agents. The current architecture is intentionally simple:

- one scanner pipeline
- one local ChromaDB collection
- one Gemini embedding client
- a compact MCP tool surface

The goal is to stay easy to run while still exposing strong multimodal retrieval behavior.

## Core Flow

### 1. Directory Preview and Scan

`parsers/scanner.py` is responsible for both:

- **previewing** a directory before indexing
- **scanning** a directory into indexable entries

The scanner:
- skips hidden files and directories by default
- skips junk directories like `node_modules`, `venv`, `dist`, `build`, and `target`
- applies optional wildcard ignores
- blocks dangerous root-level scans
- skips very large files

This is the part of the system that turns raw local files into structured index candidates.

### 2. Modality-Specific Extraction

The scanner emits entries differently depending on modality:

- **Text files**: extracted as text and chunked with overlap
- **Images / audio / video**: read as raw bytes and sent directly to Gemini Embedding 2
- **PDFs**: rendered page-by-page as images while preserving extracted page text for result readability

This means the index is not just text-first. It is a unified store of text entries and multimodal entries that all live in the same semantic space.

### 3. Metadata Model

Every indexed entry stores more than just content. It also stores metadata used for search precision and result inspection:

- source path
- filename
- extension
- directory root
- type
- modality
- chunk index
- page number
- file hash
- file size
- modification time

That metadata powers:
- compact retrieval filters
- exact file/page reporting
- context retrieval
- deduplication and sync behavior

### 4. Gemini Embedding Client

`embeddings/gemini.py` handles embedding calls to `gemini-embedding-2-preview`.

Key behaviors:
- uses `RETRIEVAL_DOCUMENT` for indexing
- uses `RETRIEVAL_QUERY` for search
- uses output dimensionality `768`
- retries quota-related failures with exponential backoff

The current retry logic uses **5 attempts**, not 3.

### 5. Local Vector Store

`db/store.py` persists the index in a local ChromaDB database under `~/.gemini_mcp_db`.

The store layer is responsible for:
- upserting vectors and metadata
- listing indexed sources and directories
- filtered query post-processing
- source-level context retrieval
- ghost-file cleanup support
- deduplication support via file hashes

The store intentionally stays simple and local. There is no hosted vector dependency.

### 6. MCP Tool Surface

`server.py` exposes the agent-facing API:

- `index_directory`
- `preview_directory`
- `search_my_documents`
- `get_result_context`
- `list_indexed_directories`
- `sync_indexed_directories`
- `remove_directory_from_index`
- `gemini://database-stats`

The design principle is:

**compact public API, smarter internal behavior**

The server should feel powerful because retrieval is precise and context-aware, not because users have to memorize dozens of parameters.

## Retrieval Model

The current retrieval flow is:

1. embed the user query with `RETRIEVAL_QUERY`
2. retrieve a broad candidate set from ChromaDB
3. apply compact metadata filters in the local store layer
4. format results with exact source and locator information
5. optionally resolve nearby context with `get_result_context`

This gives agents a clean progression from:

- semantic search
- exact file hit
- exact page/chunk context

## Intentional Non-Goals

The current architecture does **not** try to solve everything at once.

It does not yet include:
- heavy user-managed configuration
- hosted sync or remote vector storage
- expensive multimodal enrichment pipelines by default
- complex multi-index orchestration

Those can be layered later if they improve the product, but they are not required for a strong core experience.
