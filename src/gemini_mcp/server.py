import os
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from google.genai import types
from gemini_mcp.db.store import ChromaStore
from gemini_mcp.embeddings.gemini import GeminiEmbeddingClient
from gemini_mcp.parsers.scanner import scan_directory, preview_directory_scan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP Server
mcp = FastMCP("Gemini Embedding 2 MCP")

# Initialize global clients (lazy-loaded so they only instantiate on actual usage)
_db_store: Optional[ChromaStore] = None
_embedding_client: Optional[GeminiEmbeddingClient] = None


def get_db() -> ChromaStore:
    global _db_store
    if _db_store is None:
        _db_store = ChromaStore()
    return _db_store


def get_embedder() -> GeminiEmbeddingClient:
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = GeminiEmbeddingClient()
    return _embedding_client


def _format_search_result(match: dict, index: int) -> str:
    metadata = match["metadata"]
    source = metadata.get("source", "Unknown file")
    filename = metadata.get("filename") or os.path.basename(source) or "Unknown file"
    result_lines = [
        f"--- Result {index} ---",
        f"File Name: {filename}",
        f"File Path: {source}",
        f"Type: {metadata.get('type', 'unknown')}",
        f"Modality: {metadata.get('modality', 'unknown')}",
    ]

    if metadata.get("page_number") is not None:
        result_lines.append(f"Page: {metadata['page_number']}")

    result_lines.append(f"Relevance Distance: {match.get('distance', 0.0):.3f}")
    result_lines.append(f"Content:\n{match['text']}")
    return "\n".join(result_lines)


def _parse_locator(locator: str | None) -> tuple[str | None, int | None]:
    if not locator:
        return None, None

    kind, separator, raw_value = locator.partition(":")
    if separator == "" or not raw_value.isdigit():
        raise ValueError(
            "Locator must use the format 'chunk:<n>' or 'page:<n>' with a numeric index."
        )
    return kind, int(raw_value)


@mcp.tool()
async def index_directory(directory_path: str, ignore: list[str] = None) -> str:
    """
    Scans a local directory, extracts text from files (PDF, DOCX, TXT, MD) AND
    raw video/audio/image bytes, generates semantic embeddings using
    Gemini 2 and stores them for searching.

    Args:
        directory_path: Absolute path to the directory.
        ignore: Optional list of glob patterns to ignore (e.g., ["*.log", "drafts", "temp*"]).
    """
    try:
        db = get_db()
        embedder = get_embedder()

        chunks = []
        items_to_embed = []

        logger.info(f"Starting scan of {directory_path}")

        # Smart Deduplication: fetch known files and their hashes
        existing_hashes = db.get_indexed_file_hashes(directory_path)

        # Batch processing to avoid massive API payloads and spread out TPM usage
        BATCH_SIZE = 20
        total_indexed = 0

        for item in scan_directory(
            directory_path, ignore=ignore, existing_hashes=existing_hashes
        ):
            # Handle changed files by deleting their old chunks first
            if item.get("action") == "delete":
                logger.info(f"File changed, deleting old index for: {item['source']}")
                db.delete_file(item["source"])
                continue

            chunks.append(item)

            if item.get("is_media", False):
                items_to_embed.append(
                    types.Part.from_bytes(
                        data=item["raw_data"],
                        mime_type=item.get("mime_type", "application/octet-stream"),
                    )
                )
            else:
                items_to_embed.append(item["raw_data"])

            if len(chunks) >= BATCH_SIZE:
                embeddings = embedder.embed_items(items_to_embed)
                db.add_chunks(chunks, embeddings)
                total_indexed += len(chunks)
                chunks.clear()
                items_to_embed.clear()

        # Process remaining chunks
        if chunks:
            embeddings = embedder.embed_items(items_to_embed)
            db.add_chunks(chunks, embeddings)
            total_indexed += len(chunks)

        return f"Successfully indexed {total_indexed} segments (text & images) from {directory_path}. Skipped unchanged files to save tokens."

    except Exception as e:
        logger.error(f"Error during indexing: {e}")
        return f"Failed to index {directory_path}: {str(e)}"


@mcp.tool()
async def search_my_documents(
    query: str,
    limit: int = 5,
    scope: str | None = None,
    types: list[str] | None = None,
    path_prefix: str | None = None,
    extensions: list[str] | None = None,
    modalities: list[str] | None = None,
) -> str:
    """
    Performs a semantic search over your previously indexed local documents
    AND images using the Gemini 2 Embedding model.
    """
    try:
        db = get_db()
        embedder = get_embedder()

        query_vec = embedder.embed_query(query)
        if not query_vec:
            return "Failed to generate embedding for query."

        filters = {
            "scope": scope,
            "types": types,
            "path_prefix": path_prefix,
            "extensions": extensions,
            "modalities": modalities,
        }
        active_filters = {key: value for key, value in filters.items() if value}

        matches = db.query(query_vec, n_results=limit, filters=active_filters or None)

        if not matches:
            return "No relevant documents found. Have you indexed your directories yet?"

        result_word = "result" if len(matches) == 1 else "results"
        sections = [f"Found {len(matches)} relevant {result_word}:\n"]
        for i, match in enumerate(matches, 1):
            sections.append(_format_search_result(match, i))

        if active_filters:
            filters_str = ", ".join(
                f"{key}={value}" for key, value in active_filters.items()
            )
            sections.insert(0, f"Applied filters: {filters_str}\n")

        return "\n\n".join(sections)

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Error executing search: {str(e)}"


@mcp.tool()
async def preview_directory(
    directory_path: str, ignore: list[str] | None = None
) -> str:
    """
    Summarizes what would be indexed before the server performs a full scan.
    """
    preview = preview_directory_scan(directory_path, ignore=ignore)

    if preview["skip_reasons"].get("missing_directory"):
        return f"Directory not found: {directory_path}"
    if preview["skip_reasons"].get("root_blocked"):
        return f"Refusing to preview root directory: {directory_path}"

    lines = [
        f"Preview for {preview['directory']}",
        f"Eligible files: {preview['eligible_files']}",
    ]

    if preview["modality_counts"]:
        lines.append("Modalities:")
        for modality, count in sorted(preview["modality_counts"].items()):
            lines.append(f"- {modality}: {count}")

    if preview["skip_reasons"]:
        lines.append("Skipped:")
        for reason, count in sorted(preview["skip_reasons"].items()):
            lines.append(f"- {reason}: {count}")

    return "\n".join(lines)


@mcp.tool()
async def list_indexed_directories() -> str:
    """
    Lists indexed parent directories known to the database.
    """
    try:
        db = get_db()
        directories = db.list_indexed_directories()
        if not directories:
            return "The database is currently empty."

        return "The following directories are indexed:\n- " + "\n- ".join(directories)
    except Exception as e:
        return f"Error connecting to database: {str(e)}"


@mcp.tool()
async def remove_directory_from_index(directory_path: str) -> str:
    """
    Removes all documents and images belonging to a specific directory path from the index.
    """
    try:
        db = get_db()
        deleted_count = db.delete_directory(directory_path)
        return f"Successfully removed {deleted_count} chunks/images originating from {directory_path}."
    except Exception as e:
        return f"Error removing directory: {str(e)}"


@mcp.tool()
async def sync_indexed_directories() -> str:
    """
    Auto-updates existing folders. It finds all unique parent directories of currently
    indexed files and re-indexes them to capture new or modified files.
    """
    try:
        db = get_db()
        sources = db.list_indexed_sources()
        if not sources:
            return "Database is empty. Nothing to sync."
        # 1. Prune Ghost Files (Files that were deleted from disk but exist in DB)
        purged_files = 0
        purged_vectors = 0
        existing_sources = []

        for source in sources:
            if not os.path.exists(source):
                # File is gone, clear it from database
                purged_vectors += db.delete_file(source)
                purged_files += 1
            else:
                existing_sources.append(source)

        # 2. Rescan living directories
        # Find unique parent directories of existing files
        directories = set()
        for source in existing_sources:
            parent = os.path.dirname(source)
            directories.add(parent)

        # To avoid redundant scans, only keep top-level directories
        top_level_dirs = set()
        for d in sorted(list(directories)):
            if not any(d.startswith(top + os.sep) for top in top_level_dirs):
                top_level_dirs.add(d)

        results = []
        for d in top_level_dirs:
            res = await index_directory(d)
            results.append(res)

        return (
            f"Sync Summary:\n- Purged {purged_files} deleted files ({purged_vectors} vectors freed).\n"
            + "\n".join(results)
        )
    except Exception as e:
        return f"Error during sync: {str(e)}"


@mcp.tool()
async def get_result_context(
    source: str, locator: str | None = None, window: int = 1
) -> str:
    """
    Returns nearby chunks or pages for a previously indexed result.
    """
    try:
        db = get_db()
        entries = db.get_source_entries(source)
        if not entries:
            return f"No indexed content found for {source}."

        locator_kind, locator_value = _parse_locator(locator)

        target_index = 0
        if locator_kind is not None:
            for index, entry in enumerate(entries):
                metadata = entry["metadata"]
                if (
                    locator_kind == "chunk"
                    and metadata.get("chunk_index") == locator_value
                ):
                    target_index = index
                    break
                if (
                    locator_kind == "page"
                    and metadata.get("page_number") == locator_value
                ):
                    target_index = index
                    break
            else:
                return f"Could not find locator {locator} for {source}."

        start = max(0, target_index - window)
        end = min(len(entries), target_index + window + 1)
        selected = entries[start:end]

        lines = [f"Context for {source}"]
        for entry in selected:
            metadata = entry["metadata"]
            if metadata.get("page_number") is not None:
                label = f"Page {metadata['page_number']}"
            else:
                label = f"Chunk {metadata.get('chunk_index', 0)}"
            lines.append(f"--- {label} ---")
            lines.append(entry["text"])

        return "\n".join(lines)
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error retrieving context: {str(e)}"


@mcp.resource("gemini://database-stats")
def get_database_stats() -> str:
    """Returns the scale and health of the ChromaDB index for Gemini."""
    try:
        db = get_db()
        sources = db.list_indexed_sources()
        try:
            count = db.collection.count()
        except Exception:
            count = "Unknown"

        return f"Database stats:\n- Total Indexed Vector Segments: {count}\n- Total Indexed Parent Files: {len(sources)}\n"
    except Exception as e:
        return f"Database unavailable: {str(e)}"


def main():
    """Entry point for the MCP server when run as a script."""
    mcp.run()


if __name__ == "__main__":
    main()
