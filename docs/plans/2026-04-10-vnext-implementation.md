# Gemini Embedding 2 MCP Server vNext Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade the server into a stronger multimodal local memory MCP with better retrieval precision, result context, richer metadata, preview tooling, and clearer docs.

**Architecture:** Preserve the current local-first single-index design, but add richer metadata at ingestion time, query-side filtering in the store layer, and two new agent-facing tools (`preview_directory`, `get_result_context`). Keep configuration implicit by default and expose only compact per-call overrides.

**Tech Stack:** Python, `mcp`, `google-genai`, ChromaDB, PyMuPDF, python-docx, pytest, Markdown docs.

---

### Task 1: Define and Test the New Retrieval Surface

**Files:**
- Modify: `tests/test_gemini.py`
- Modify: `tests/test_scanner.py`

**Steps:**
1. Add failing tests for filtered retrieval arguments and result formatting.
2. Add failing tests for `preview_directory()` summaries and skip reasons.
3. Add failing tests for `get_result_context()` using chunk/page locators.
4. Add failing tests verifying directory listing semantics return directories, not files.
5. Run targeted pytest commands and confirm failures are for missing behavior.

### Task 2: Expand Scan Metadata and Preview Support

**Files:**
- Modify: `src/gemini_mcp/parsers/scanner.py`
- Modify: `tests/test_scanner.py`

**Steps:**
1. Add richer metadata for each scanned item:
   - `filename`
   - `extension`
   - `directory_root`
   - `modality`
   - `page_number`
   - `mtime`
   - `size_bytes`
2. Add a reusable preview mode or helper that summarizes what would be indexed.
3. Preserve current guardrails and dedup behavior.
4. Run scanner tests and get them green.

### Task 3: Expand Store Query and Context Capabilities

**Files:**
- Modify: `src/gemini_mcp/db/store.py`
- Modify: `tests/test_gemini.py`

**Steps:**
1. Add helpers for:
   - filtered query post-processing
   - fetching unique indexed directories
   - fetching chunks/pages for a source
2. Implement compact filter support:
   - `scope`
   - `types`
   - `path_prefix`
   - `extensions`
3. Implement context lookup helpers for neighboring chunks/pages.
4. Run targeted tests and make them pass.

### Task 4: Upgrade the MCP Tool Surface

**Files:**
- Modify: `src/gemini_mcp/server.py`
- Modify: `tests/test_gemini.py`

**Steps:**
1. Extend `search_my_documents()` with compact optional filters.
2. Add `preview_directory()`.
3. Add `get_result_context()`.
4. Make `list_indexed_directories()` actually return indexed directory roots.
5. Keep `sync_indexed_directories()` working with the updated listing behavior.
6. Run server-related tests and make them pass.

### Task 5: Improve Docs and Product Positioning

**Files:**
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/multimodality.md`
- Modify: `docs/agent-guardrails.md`
- Create: `docs/use-cases.md`
- Create: `docs/result-model.md`
- Modify: `CHANGELOG.md`

**Steps:**
1. Rewrite README positioning around multimodal local memory.
2. Document the new tools and compact filtering model.
3. Update architecture docs so implementation details match the code.
4. Add practical use cases and result model docs.
5. Add changelog entry for the vNext release.

### Task 6: Verify End-to-End

**Files:**
- Verify only

**Steps:**
1. Run the full test suite with `uv run pytest`.
2. Review the final diff for accidental churn.
3. Confirm docs and tool signatures are aligned.
4. Summarize any remaining limitations for later work.
