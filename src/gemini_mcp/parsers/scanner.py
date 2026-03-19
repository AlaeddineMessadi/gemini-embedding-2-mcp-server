import os
import pathlib
import logging
from typing import List, Generator, Dict, Any

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    
import fnmatch

try:
    import docx
except ImportError:
    docx = None

logger = logging.getLogger(__name__)

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
        if ext in ['.txt', '.md', '.csv']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
                
        elif ext == '.docx' and docx is not None:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
            
        else:
            logger.debug(f"Unsupported or missing library for file type: {ext}")
            return ""
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""

def scan_directory(directory_path: str, chunk_size: int = 1000, overlap: int = 200, ignore: list = None) -> Generator[Dict[str, Any], None, None]:
    """
    Recursively scans a directory, extracts text from supported files or raw bytes from images, 
    and yields content ready for multimodal embedding.
    Yields dicts with: {'raw_data': Any, 'is_image': bool, 'metadata': {'source': str, 'chunk_index': int, 'type': str}}
    """
    ignore = ignore or []
    
    base_dir = pathlib.Path(directory_path)
    if not base_dir.exists() or not base_dir.is_dir():
        logger.error(f"Directory not found: {directory_path}")
        return
        
    abs_path = str(base_dir.absolute())
    if abs_path in ["/", "/Users", "/home", "C:\\", "D:\\"]:
        logger.error(f"Safety constraint: Cannot scan operating system root directory {abs_path}")
        return
        
    media_extensions = {
        '.jpg', '.jpeg', '.png', '.webp', # Images
        '.mp4',                           # Video
        '.mp3', '.wav', '.aiff', '.aac'   # Audio
    }
        
    IGNORE_DIRS = {
        # Python
        "__pycache__", "venv", "env", 
        # JavaScript / Web
        "node_modules", "bower_components",
        # Build / Output / Compiled
        "build", "dist", "out", "target", "bin", "obj",
        # Dependencies / Packages
        "vendor", "packages", "pkg",
        # Temp, Cache & Coverage
        "tmp", "temp", "coverage", "cache"
    }
    # Note: All hidden directories (starting with '.') like .git, .venv, .next are automatically skipped.
    MAX_FILES_PER_SCAN = 2000
    files_scanned = 0
        
    for root, dirs, files in os.walk(base_dir):
        # Modify dirs in-place to prevent os.walk from entering ignored directories
        dirs[:] = [
            d for d in dirs 
            if not d.startswith('.') 
            and d not in IGNORE_DIRS
            and not any(fnmatch.fnmatch(d, p) for p in ignore)
        ]
            
        for file in files:
            # Skip hidden files
            if file.startswith('.'):
                continue
                
            # Skip files matching custom ignore patterns
            if any(fnmatch.fnmatch(file, p) for p in ignore):
                continue
                
            if files_scanned >= MAX_FILES_PER_SCAN:
                logger.warning(f"Reached safety limit of {MAX_FILES_PER_SCAN} files per scan. Stopping.")
                return
            
            files_scanned += 1
            file_path = pathlib.Path(root) / file
            ext = file_path.suffix.lower()
            
            # Simple size check to avoid absolutely massive binaries
            try:
                if file_path.stat().st_size > 50 * 1024 * 1024:  # 50 MB limit
                    continue
            except Exception:
                continue

            # Process Media Files (Images, Video, Audio)
            if ext in media_extensions:
                try:
                    with open(file_path, "rb") as media_file:
                        mime_type = "application/octet-stream"
                        media_type = "media"
                        
                        if ext in ['.jpg', '.jpeg']: mime_type, media_type = "image/jpeg", "image"
                        elif ext == ".png": mime_type, media_type = "image/png", "image"
                        elif ext == ".webp": mime_type, media_type = "image/webp", "image"
                        elif ext == ".mp4": mime_type, media_type = "video/mp4", "video"
                        elif ext == ".mp3": mime_type, media_type = "audio/mp3", "audio"
                        elif ext == ".wav": mime_type, media_type = "audio/wav", "audio"
                        elif ext == ".aiff": mime_type, media_type = "audio/aiff", "audio"
                        elif ext == ".aac": mime_type, media_type = "audio/aac", "audio"
                        
                        yield {
                            "raw_data": media_file.read(),
                            "is_media": True,
                            "mime_type": mime_type,
                            "metadata": {
                                "source": str(file_path.absolute()),
                                "chunk_index": 0,
                                "type": media_type
                            },
                        }
                except Exception as e:
                    logger.error(f"Error reading media {file_path}: {e}")
                continue

            # Process PDF Files Visually (Page by Page)
            if ext == '.pdf' and fitz is not None:
                try:
                    doc = fitz.open(file_path)
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        
                        # Render the PDF page to a high-quality Image (PNG)
                        # This allows Gemini 2 to visually embed plots, charts, and exact layout!
                        pix = page.get_pixmap(dpi=150)
                        png_bytes = pix.tobytes("png")
                        
                        # Extract raw text for ChromaDB storage so Claude gets the actual text back upon search
                        page_text = page.get_text()
                        
                        yield {
                            "raw_data": png_bytes,
                            "is_media": True,
                            "mime_type": "image/png",
                            "text": f"--- Page {page_num + 1} from {file_path.name} ---\n{page_text}",
                            "metadata": {
                                "source": str(file_path.absolute()),
                                "chunk_index": page_num,
                                "type": "pdf_visual_page"
                            }
                        }
                except Exception as e:
                    logger.error(f"Error processing visual PDF {file_path}: {e}")
                continue

            # Process Standard Text Files (.txt, .md, .docx, .csv)
            text = extract_text_from_file(file_path)
            if not text.strip():
                continue
                
            chunks = chunk_text(text, chunk_size, overlap)
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    yield {
                        "raw_data": chunk,
                        "is_media": False,
                        "mime_type": "text/plain",
                        "metadata": {
                            "source": str(file_path.absolute()),
                            "chunk_index": i,
                            "type": "text"
                        }
                    }
