# Gemini Embedding 2 MCP Server

A powerful Model Context Protocol (MCP) server that connects your local documents to Claude (or any MCP-compatible AI) using Google's state-of-the-art **Gemini Embedding 2 Preview** model.

## Features
- **Local Vector Database**: Uses ChromaDB entirely locally to index your document embeddings.
- **Enterprise-Grade Embeddings**: Uses `gemini-embedding-2-preview` with specialized Task Types (`RETRIEVAL_DOCUMENT`) and MRL dimensionality optimization.
- **Ultimate Multimodality**: Natively scans, embeds, and mathematically retrieves **Images** (`.jpg`, `.png`, `.webp`), **Video** (`.mp4`), and **Audio** (`.mp3`, `.wav`)! Search your memories visually and sonically.
- **Visual PDF RAG**: Parses each page of a PDF as a high-quality image. Gemini semantically embeds the charts, plots, and layout visually, while returning the actual extracted text to Claude during search. It's the ultimate hybrid!
- **Dynamic File Indexing**: Read, parse, and embed TXT, MD, DOCX files directly from Claude's interface.
- **Semantic Search**: Native MCP tool for lighting-fast semantic retrieval over your multimodal files.

## Installation

This project uses [`uv`](https://github.com/astral-sh/uv) for lightning-fast Python dependency management.

```bash
# Clone the repository
git clone https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git
cd gemini-embedding-2-mcp-server

# Install dependencies
uv sync
```

## Setup & Configuration

1. **Get a Gemini API Key**: Grab one from Google AI Studio.
2. **Configure Claude Desktop**:
   Open your Claude Desktop config file (usually `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS) and add:

```json
{
  "mcpServers": {
    "gemini-embedding-2-mcp": {
      "command": "/path/to/gemini-embedding-2-mcp-server/.venv/bin/gemini-embedding-2-mcp",
      "args": [],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Available MCP Tools & Resources

### MCP Tools
Once connected, Claude will have access to:
- `index_directory(path: str)`: Scan and structurally embed a local folder (reads text, images, video, and audio natively).
- `search_my_documents(query: str, limit: int)`: Perform semantic search over your indexed documents and media.
- `list_indexed_directories()`: See what files have been embedded.
- `sync_indexed_directories()`: Automatically re-indexes known folders to capture newly added files.
- `remove_directory_from_index(path: str)`: Remove a folder's vectors from your ChromaDB instance.

### MCP Resources
Claude can instantly inspect the health and scale of your database without invoking a tool call via:
- `gemini://database-stats`: Returns the total count of vectorized segments and indexed files.

## License
MIT
