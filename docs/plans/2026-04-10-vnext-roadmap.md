# Gemini Embedding 2 MCP Server vNext Roadmap

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Turn the server from a strong local RAG utility into the clearest multimodal local memory MCP built around Gemini Embedding 2.

**Architecture:** Keep the current single-server, local-first architecture, but upgrade it in three layers: richer metadata, smarter retrieval, and modality-aware enrichment. Avoid exposing large config surfaces by default; instead, improve the server's automatic behavior and offer only a few high-value overrides.

**Tech Stack:** Python, `mcp`, `google-genai`, ChromaDB, PyMuPDF, python-docx, local filesystem scanning, Docker, GitHub docs/releases.

---

## Product Direction

The next version should not compete as "another local document indexer." The product should be known for one thing:

**A multimodal local memory engine for AI agents powered by Gemini Embedding 2.**

That positioning is stronger than "RAG" because it highlights what is actually unique:
- One embedding space across text, PDF pages, images, audio, and video
- Local-first privacy with persistent memory
- Agent-oriented indexing and retrieval flows
- Useful results without heavy manual configuration

## Core Principles

1. **Zero-config first**
   The default experience should work well without config files or tuning.

2. **Precision without complexity**
   Retrieval should become more targeted via metadata and a small number of optional filters, not a giant settings surface.

3. **Multimodal means retrieval and context**
   Indexing media is not enough. Users need exact file, page, segment, and result context.

4. **Agent-native UX**
   Tools should help agents explore, narrow, inspect, and sync, not just "index" and "search."

5. **Docs are part of the product**
   The repo must explain why this server is different, not just how to install it.

---

## Version Theme

**Suggested release theme:** `v1.2.0 - Multimodal Precision`

This should be a focused release that makes retrieval much more precise and makes the multimodal story obvious in both behavior and docs.

Do not try to ship every possible feature in one release. The fastest path to a stronger product is:
- improve retrieval controls
- improve result/context fidelity
- improve metadata
- improve docs and examples

---

## Roadmap Overview

### Phase 1: Retrieval Precision

**Outcome:** Users can ask for exactly what they want without manual configuration or broad, noisy search results.

**Features:**
- Extend `search_my_documents()` with a compact optional filter surface:
  - `scope`
  - `types`
  - `path_prefix`
  - `extensions`
  - `limit`
- Add result metadata to every hit:
  - file name
  - absolute path
  - modality
  - page number or segment index where relevant
  - distance
- Normalize terminology:
  - rename or fix `list_indexed_directories()` so it accurately describes what it returns
- Improve ranking output formatting:
  - group by modality when results are mixed
  - make result boundaries clean for agents

**Why first:**
- Lowest implementation risk
- Immediate user value
- Makes the current engine feel much more powerful without architectural churn

**Files likely involved:**
- `src/gemini_mcp/server.py`
- `src/gemini_mcp/db/store.py`
- `src/gemini_mcp/parsers/scanner.py`
- `tests/test_gemini.py`
- `README.md`

### Phase 2: Context Retrieval

**Outcome:** A result is no longer just "a path that matched." The agent can inspect the exact surrounding content.

**Features:**
- Add `get_result_context(source, locator=None, window=1)`
- Return nearby text chunks for text files
- Return explicit page references for PDFs
- Return segment references for media when available
- Add clearer document locators:
  - `page_number`
  - `chunk_index`
  - `segment_start`
  - `segment_end`

**Why second:**
- This is the missing bridge between retrieval and usefulness
- It materially improves agent answers and citations

**Files likely involved:**
- `src/gemini_mcp/server.py`
- `src/gemini_mcp/db/store.py`
- `tests/test_gemini.py`
- `README.md`
- `docs/architecture.md`

### Phase 3: Better Metadata and Smart Defaults

**Outcome:** The server becomes more accurate without asking users to configure everything manually.

**Features:**
- Store richer metadata per indexed item:
  - `filename`
  - `extension`
  - `directory_root`
  - `modality`
  - `page_number`
  - `mtime`
  - `size_bytes`
  - `file_hash`
- Add internal query heuristics:
  - visual queries bias image/PDF visual results
  - document queries bias text/PDF text-backed results
  - recent files can be optionally prioritized
- Add `preview_directory(path, ignore=None)`
  - dry-run summary before indexing
  - counts by file type and modality
  - skipped file reasons

**Why third:**
- Makes the server feel smart while keeping the public API simple
- Gives users confidence before large scans

**Files likely involved:**
- `src/gemini_mcp/parsers/scanner.py`
- `src/gemini_mcp/db/store.py`
- `src/gemini_mcp/server.py`
- `tests/test_scanner.py`
- `README.md`
- `docs/agent-guardrails.md`

### Phase 4: Media Segmentation and Enrichment

**Outcome:** The server starts using Gemini Embedding 2 more like a multimodal engine than a file-level retriever.

**Features:**
- Segment long audio files instead of embedding the entire file as one unit
- Segment video by frame interval or scene sampling
- Store optional text enrichment for media:
  - image captions
  - OCR snippets
  - audio transcript snippets
  - video scene summaries
- Preserve both:
  - raw multimodal embedding
  - agent-friendly semantic text metadata

**Why fourth:**
- Highest upside for product differentiation
- Highest complexity and token-cost sensitivity
- Should only come after metadata and retrieval structure are sound

**Files likely involved:**
- `src/gemini_mcp/parsers/scanner.py`
- `src/gemini_mcp/embeddings/gemini.py`
- `src/gemini_mcp/db/store.py`
- `src/gemini_mcp/server.py`
- new tests for segmentation logic
- `docs/multimodality.md`

### Phase 5: Packaging, Distribution, and Recognition

**Outcome:** The product is easier to discover, easier to trust, and easier to compare against weaker MCPs.

**Features:**
- Finalize Glama submission and score visibility
- Add release notes with product language, not only engineering diffs
- Add one high-signal GIF or screenshot sequence for:
  - PDF page retrieval
  - image search
  - multimodal result explanation
- Add comparison language in docs:
  - why this is different from text-only local RAG
  - why Gemini Embedding 2 matters
- Add a short "best for" section:
  - researchers
  - designers with local image libraries
  - developers searching code/docs/media together

**Why fifth:**
- Shipping a strong product without explaining it wastes the work
- Discovery and positioning are now part of MCP adoption

**Files likely involved:**
- `README.md`
- `CHANGELOG.md`
- `docs/architecture.md`
- `docs/multimodality.md`
- `assets/`

---

## Recommended Tool Surface For vNext

Keep the tool set compact. Recommended public surface:

- `index_directory(path: str, ignore: list[str] | None = None)`
- `preview_directory(path: str, ignore: list[str] | None = None)`
- `search_my_documents(query: str, limit: int = 5, scope: str | None = None, types: list[str] | None = None, path_prefix: str | None = None, extensions: list[str] | None = None)`
- `get_result_context(source: str, locator: str | None = None, window: int = 1)`
- `list_indexed_directories()`
- `sync_indexed_directories()`
- `remove_directory_from_index(path: str)`

The API remains simple, but the server becomes far more capable.

---

## Documentation Plan

The docs need to shift from "installation plus claims" to "installation plus proof."

### README Changes

Update `README.md` to include:
- a sharper one-line positioning statement
- a "Why this is different" section
- 3 concrete use cases:
  - search across code + PDFs
  - search image/video libraries by meaning
  - retrieve exact page/path context for agents
- a "How it thinks" section:
  - visual PDF retrieval
  - multimodal file embeddings
  - local persistence and sync
- one section for advanced but optional filters

### Architecture Doc Changes

Update `docs/architecture.md` to reflect the real code and upcoming direction:
- note current metadata model
- explain retrieval flow end-to-end
- document locator concepts
- fix any stale statements
  - for example, retry/backoff behavior should match the implementation exactly

### Multimodality Doc Changes

Update `docs/multimodality.md` to move beyond general claims:
- explain file-level vs page-level vs segment-level indexing
- explain why enrichment helps agent answers
- show examples of cross-modal retrieval

### Guardrails Doc Changes

Update `docs/agent-guardrails.md` to include:
- dry-run indexing behavior if `preview_directory` ships
- default scan safety rules
- what gets skipped and why
- how smart defaults reduce risk without requiring user config

### New Docs To Add

Create:
- `docs/use-cases.md`
- `docs/result-model.md`
- `docs/roadmap.md` or keep this plan under `docs/plans/`

---

## "Make It Known" Plan

This part matters. Good MCPs often fail because the repo explains features, but not identity.

### Messaging

Use a tighter, repeatable description everywhere:

**Primary message:**
`A multimodal local memory MCP for AI agents powered by Gemini Embedding 2.`

**Supporting message:**
`Search local text, PDFs, images, audio, and video in one embedding space, with exact file and page context.`

### Proof Assets

Before the next public push, prepare:
- one example with a PDF chart being retrieved semantically
- one example with an image or video result
- one example with exact file path + page context

### Distribution Targets

For the next release, update:
- GitHub release notes
- README hero section
- Glama listing description
- Awesome MCP PR/comment if needed
- MCP-related directories or registries you care about

### Social Proof

Add a short "Use Cases" section and real examples so users can immediately picture where the server fits.

---

## Release Sequence

Recommended release sequence:

1. `v1.2.0`
   Retrieval precision, `preview_directory`, better metadata, context retrieval, docs refresh

2. `v1.3.0`
   Media segmentation and modality-aware enrichment

3. `v1.4.0`
   Advanced ranking heuristics, optional lightweight config profiles, more observability

Do not skip directly to heavy config. Improve behavior first.

---

## Risks To Avoid

- Adding too many knobs and turning the server into a configuration burden
- Adding enrichment before result/context structure is sound
- Expanding the tool surface faster than the docs
- Using "multimodal" in marketing without showing multimodal retrieval examples
- Letting docs drift from implementation details

---

## Immediate Next Version Recommendation

If only one release is planned next, ship this:

### v1.2.0 Scope

- Smarter `search_my_documents()` with compact filters
- `preview_directory()`
- `get_result_context()`
- richer metadata including page-aware PDF metadata
- clearer result formatting
- README rewrite around multimodal local memory
- architecture and multimodality doc refresh
- release notes and Glama-ready positioning

That is the best next version because it improves:
- power
- clarity
- docs
- launch story

without overcomplicating the user experience.
