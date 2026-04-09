# Result Model

Each indexed entry stores both retrievable content and metadata that help agents narrow, explain, and inspect results precisely.

## Stored Metadata

Every indexed item stores:

- `source`: Absolute source file path
- `filename`: Basename of the source file
- `extension`: Lowercase file extension
- `directory_root`: The indexed root directory that produced the entry
- `chunk_index`: Zero-based chunk or page position
- `page_number`: One-based PDF page number when applicable, otherwise `null`
- `type`: Entry type such as `text`, `image`, `audio`, `video`, or `pdf_visual_page`
- `modality`: Broad modality category such as `text`, `pdf`, `image`, `audio`, or `video`
- `file_hash`: MD5 hash used for deduplication and sync
- `mtime`: File modification timestamp
- `size_bytes`: File size in bytes

## Search Output

`search_my_documents()` returns formatted entries that include:

- file name
- file path
- type
- modality
- page number when available
- relevance distance
- stored content text

This makes the results agent-readable without requiring another lookup just to identify the source.

## Context Output

`get_result_context()` returns the nearby stored entries for a source file:

- neighboring text chunks for text-based files
- exact PDF page references for PDF entries

This is designed to help an agent move from:

1. `search result`
2. `exact file and location`
3. `local surrounding context`

without rebuilding the retrieval chain itself.
