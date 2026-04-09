import os
import pathlib
import logging
from collections import defaultdict
from typing import List, Generator, Dict, Any

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

import fnmatch
import hashlib

try:
    import docx
except ImportError:
    docx = None

logger = logging.getLogger(__name__)

MEDIA_TYPES = {
    ".jpg": ("image/jpeg", "image"),
    ".jpeg": ("image/jpeg", "image"),
    ".png": ("image/png", "image"),
    ".webp": ("image/webp", "image"),
    ".mp4": ("video/mp4", "video"),
    ".mp3": ("audio/mp3", "audio"),
    ".wav": ("audio/wav", "audio"),
    ".aiff": ("audio/aiff", "audio"),
    ".aac": ("audio/aac", "audio"),
}

IGNORE_DIRS = {
    "__pycache__",
    "venv",
    "env",
    "node_modules",
    "bower_components",
    "build",
    "dist",
    "out",
    "target",
    "bin",
    "obj",
    "vendor",
    "packages",
    "pkg",
    "tmp",
    "temp",
    "coverage",
    "cache",
}

ROOT_BLOCKLIST = {"/", "/Users", "/home", "C:\\", "D:\\"}
MAX_FILES_PER_SCAN = 2000
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Splits text into overlapping chunks for better semantic retrieval."""
    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


def extract_text_from_file(file_path: pathlib.Path) -> str:
    """Extracts raw text from a given file based on its extension."""
    ext = file_path.suffix.lower()

    try:
        if ext in [".txt", ".md", ".csv"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        elif ext == ".docx" and docx is not None:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])

        else:
            logger.debug(f"Unsupported or missing library for file type: {ext}")
            return ""
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""


def compute_file_hash(file_path: pathlib.Path) -> str:
    """Computes an MD5 hash of the file contents."""
    md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            # Read in 1MB chunks to avoid excessive memory on large files
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                md5.update(chunk)
    except Exception as e:
        logger.error(f"Error hashing file {file_path}: {e}")
        return ""
    return md5.hexdigest()


def _build_metadata(
    file_path: pathlib.Path,
    base_dir: pathlib.Path,
    *,
    chunk_index: int,
    file_hash: str,
    file_type: str,
    modality: str,
    page_number: int | None = None,
) -> Dict[str, Any]:
    stat = file_path.stat()
    return {
        "source": str(file_path.absolute()),
        "filename": file_path.name,
        "extension": file_path.suffix.lower(),
        "directory_root": str(base_dir.absolute()),
        "chunk_index": chunk_index,
        "page_number": page_number,
        "type": file_type,
        "modality": modality,
        "file_hash": file_hash,
        "mtime": stat.st_mtime,
        "size_bytes": stat.st_size,
    }


def _walk_directory(
    directory_path: str, ignore: list | None = None
) -> tuple[list[Dict[str, Any]], Dict[str, Any]]:
    ignore = ignore or []

    base_dir = pathlib.Path(directory_path)
    summary = {
        "directory": str(base_dir.absolute()),
        "eligible_files": 0,
        "modality_counts": defaultdict(int),
        "skip_reasons": defaultdict(int),
    }

    if not base_dir.exists() or not base_dir.is_dir():
        logger.error(f"Directory not found: {directory_path}")
        summary["skip_reasons"]["missing_directory"] += 1
        return [], summary

    abs_path = str(base_dir.absolute())
    if abs_path in ROOT_BLOCKLIST:
        logger.error(
            f"Safety constraint: Cannot scan operating system root directory {abs_path}"
        )
        summary["skip_reasons"]["root_blocked"] += 1
        return [], summary

    candidates = []
    files_scanned = 0

    for root, dirs, files in os.walk(base_dir):
        filtered_dirs = []
        for directory_name in dirs:
            if directory_name.startswith("."):
                summary["skip_reasons"]["hidden_directory"] += 1
                continue
            if directory_name in IGNORE_DIRS or any(
                fnmatch.fnmatch(directory_name, pattern) for pattern in ignore
            ):
                summary["skip_reasons"]["ignored_directory"] += 1
                continue
            filtered_dirs.append(directory_name)
        dirs[:] = filtered_dirs

        for file_name in files:
            if file_name.startswith("."):
                summary["skip_reasons"]["hidden"] += 1
                continue

            if any(fnmatch.fnmatch(file_name, pattern) for pattern in ignore):
                summary["skip_reasons"]["custom_ignore"] += 1
                continue

            if files_scanned >= MAX_FILES_PER_SCAN:
                logger.warning(
                    f"Reached safety limit of {MAX_FILES_PER_SCAN} files per scan. Stopping."
                )
                summary["skip_reasons"]["scan_limit"] += 1
                return candidates, summary

            files_scanned += 1
            file_path = pathlib.Path(root) / file_name

            try:
                stat = file_path.stat()
            except Exception:
                summary["skip_reasons"]["stat_error"] += 1
                continue

            if stat.st_size > MAX_FILE_SIZE_BYTES:
                summary["skip_reasons"]["too_large"] += 1
                continue

            ext = file_path.suffix.lower()
            file_hash = compute_file_hash(file_path)

            candidate = {
                "path": file_path,
                "extension": ext,
                "file_hash": file_hash,
                "mtime": stat.st_mtime,
                "size_bytes": stat.st_size,
            }

            if ext in MEDIA_TYPES:
                candidate["modality"] = MEDIA_TYPES[ext][1]
            elif ext == ".pdf":
                if fitz is None:
                    summary["skip_reasons"]["missing_pdf_support"] += 1
                    continue
                candidate["modality"] = "pdf"
            else:
                text = extract_text_from_file(file_path)
                if not text.strip():
                    summary["skip_reasons"]["unsupported"] += 1
                    continue
                candidate["modality"] = "text"
                candidate["text"] = text

            candidates.append(candidate)
            summary["eligible_files"] += 1
            summary["modality_counts"][candidate["modality"]] += 1

    return candidates, summary


def preview_directory_scan(
    directory_path: str, ignore: list | None = None
) -> Dict[str, Any]:
    candidates, summary = _walk_directory(directory_path, ignore=ignore)
    summary["candidates"] = [
        str(candidate["path"].absolute()) for candidate in candidates
    ]
    summary["modality_counts"] = dict(summary["modality_counts"])
    summary["skip_reasons"] = dict(summary["skip_reasons"])
    return summary


def scan_directory(
    directory_path: str,
    chunk_size: int = 1000,
    overlap: int = 200,
    ignore: list = None,
    existing_hashes: dict = None,
) -> Generator[Dict[str, Any], None, None]:
    """
    Recursively scans a directory, extracts text from supported files or raw bytes from images,
    and yields content ready for multimodal embedding.
    Yields dicts with: {'raw_data': Any, 'is_image': bool, 'metadata': {'source': str, 'chunk_index': int, 'type': str}}
    """
    ignore = ignore or []
    base_dir = pathlib.Path(directory_path)
    candidates, _ = _walk_directory(directory_path, ignore=ignore)

    for candidate in candidates:
        file_path = candidate["path"]
        source_str = str(file_path.absolute())
        file_hash = candidate["file_hash"]

        if existing_hashes and source_str in existing_hashes:
            if existing_hashes[source_str] == file_hash and file_hash != "":
                continue
            yield {"action": "delete", "source": source_str}

        ext = candidate["extension"]
        modality = candidate["modality"]

        if ext in MEDIA_TYPES:
            try:
                with open(file_path, "rb") as media_file:
                    mime_type, media_type = MEDIA_TYPES[ext]
                    yield {
                        "raw_data": media_file.read(),
                        "is_media": True,
                        "mime_type": mime_type,
                        "metadata": _build_metadata(
                            file_path,
                            base_dir,
                            chunk_index=0,
                            file_hash=file_hash,
                            file_type=media_type,
                            modality=modality,
                        ),
                    }
            except Exception as e:
                logger.error(f"Error reading media {file_path}: {e}")
            continue

        if ext == ".pdf" and fitz is not None:
            try:
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(dpi=150)
                    png_bytes = pix.tobytes("png")
                    page_text = page.get_text()

                    yield {
                        "raw_data": png_bytes,
                        "is_media": True,
                        "mime_type": "image/png",
                        "text": f"--- Page {page_num + 1} from {file_path.name} ---\n{page_text}",
                        "metadata": _build_metadata(
                            file_path,
                            base_dir,
                            chunk_index=page_num,
                            page_number=page_num + 1,
                            file_hash=file_hash,
                            file_type="pdf_visual_page",
                            modality=modality,
                        ),
                    }
            except Exception as e:
                logger.error(f"Error processing visual PDF {file_path}: {e}")
            continue

        text = candidate.get("text", "")
        if not text.strip():
            continue

        chunks = chunk_text(text, chunk_size, overlap)
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                yield {
                    "raw_data": chunk,
                    "is_media": False,
                    "mime_type": "text/plain",
                    "metadata": _build_metadata(
                        file_path,
                        base_dir,
                        chunk_index=i,
                        file_hash=file_hash,
                        file_type="text",
                        modality=modality,
                    ),
                }
