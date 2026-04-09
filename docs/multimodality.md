# Ultimate Multimodality

Gemini Embedding 2 is valuable because it does not force your knowledge into a text-only pipeline. This server is designed around that property.

## What "Multimodal" Means Here

The server can currently index:

- **Text**: `.txt`, `.md`, `.csv`, `.docx`
- **PDFs**: page-by-page visual embeddings with extracted page text
- **Images**: `.jpg`, `.jpeg`, `.png`, `.webp`
- **Audio**: `.mp3`, `.wav`, `.aiff`, `.aac`
- **Video**: `.mp4`

All of these end up in one local semantic memory layer.

## Native Media Retrieval

For images, audio, and video, the server sends raw bytes to Gemini Embedding 2 through `types.Part.from_bytes(...)`.

That means the system is not limited to OCR, filenames, or transcripts. A query can retrieve a file because of what the media **contains**, not only because of text extracted from it.

This is especially useful when your workspace includes:
- design screenshots
- exported charts
- recordings
- short clips
- mixed-format project archives

## Visual PDF Retrieval

PDFs are handled differently from standard text files.

Instead of flattening the whole document into plain text only, the server:

1. renders each page as an image
2. embeds that page visually
3. stores extracted text as the readable result payload
4. stores the exact `page_number` for context retrieval

This gives you two benefits at once:

- the retrieval quality of a visual page representation
- the usability of readable page text in the result

## Why Page-Aware Metadata Matters

Multimodal retrieval is only genuinely useful if the result can be traced back to a precise local location.

That is why the server now stores metadata such as:
- `modality`
- `type`
- `page_number`
- `extension`
- `directory_root`
- `filename`

This enables:
- modality filters
- page-aware citations
- scoped search
- context lookups after retrieval

## Current Strengths

The strongest parts of the multimodal design today are:

- one memory layer across multiple modalities
- visual PDF page indexing
- direct media embeddings
- exact file and page reporting

## Current Limits

The current implementation still indexes audio and video at the file level, not at fine-grained scene or transcript segment level.

That means:
- you can retrieve the right file semantically
- but the system may not yet isolate the exact timestamp inside a long recording

This is a good foundation, but segment-level media enrichment is a later upgrade, not a current claim.
