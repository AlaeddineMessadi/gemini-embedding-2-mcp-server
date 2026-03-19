# Architecture

The `gemini-embedding-2-mcp-server` is built with simplicity, local privacy, and state-of-the-art multimodal performance in mind.

## Core Flow
1. **Document Ingestion & Guardrails (`parsers/scanner.py`)**:
   Recursively reads through a directory, skipping huge binary files and using an intelligent **Agentic Guardrail** to skip junk folders (`node_modules`, `venv`, `build`) and any dynamically passed wildcards.

2. **Multimodal & Visual RAG Extraction (`parsers/scanner.py`)**:
   - **Text**: Standard chunking (1000 characters, 200 overlap).
   - **Media**: Extracts raw bytes and MIME types for Images, Video, and Audio.
   - **True Visual PDFs**: `PyMuPDF` renders every page of a PDF as a high-definition image to capture tables, charts, and layout visually, while returning raw text as a fallback.

3. **Intelligent Embedding (`embeddings/gemini.py`)**:
   Sends batches of strings or multimodal byte parts to `gemini-embedding-2-preview` via the `google-genai` SDK.
   - **Task Types**: Dynamically applies `RETRIEVAL_DOCUMENT` for scanning and `RETRIEVAL_QUERY` for searching.
   - **MRL (Dimensionality)**: Vectors are optimized to a `768` dimension mathematically for reduced storage overhead with zero accuracy sacrifice.
   - **API Backoff**: Features a 3-try exponential backoff loop to elegantly handle `429 Rate Limits` from Google.

4. **Vector Storage (`db/store.py`)**:
   The vectors and raw data are stored entirely locally in a persistent `chromadb` instance (`~/.gemini_mcp_db`), ensuring your file contents never leave your machine except for the minimal API embedding call.
   - Features **Ghost File Purging** to automatically remove missing vectors during syncs.

5. **MCP Server (`server.py`)**:
   Uses the `mcp` framework to seamlessly expose tools like `index_directory`, `search_my_documents`, `list_indexed_directories`, and `sync_indexed_directories` directly to Claude Desktop!
