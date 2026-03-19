<div align="center">
  <img src="assets/banner.svg" alt="Gemini Embedding 2 MCP Server Banner" />

  <p align="center">
    <strong>A powerful Model Context Protocol (MCP) server that transforms any local directory into an ultrafast, visually-aware spatial search engine for AI agents.</strong>
  </p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
  [![MCP](https://img.shields.io/badge/MCP-Compatible-8A2BE2.svg)](https://modelcontextprotocol.io/)
</div>

---

Connect your local documents, code, images, and videos directly to **Claude**, **Cursor**, or **VS Code** using Google's state-of-the-art `gemini-embedding-2-preview` model and a strictly local **ChromaDB** vector database.

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| 🛡️ **Local Privacy** | Uses ChromaDB entirely locally (`~/.gemini_mcp_db`). Your files never go to a 3rd party database. Only raw byte chunks are sent to the Gemini Embedding API. |
| 🧠 **Enterprise-Grade** | Leverages `gemini-embedding-2-preview` with specialized `RETRIEVAL_DOCUMENT` Task Types and MRL `768` dimensionality optimization. |
| 📸 **Ultimate Multimodality** | Natively scans, embeds, and retrieves **Images** (`.jpg`, `.webp`), **Video** (`.mp4`), and **Audio** (`.mp3`, `.wav`) without extracting text! |
| 📄 **Visual PDF RAG** | Parses PDFs page-by-page as high-quality images. It visually embeds charts, plots, and layout while preserving extracted text for LLM citation. |
| 🤖 **Agentic Guardrails** | Built for autonomous AI agents. Includes an automatic Junk Filter (`node_modules`, `.git`), wildcard blacklisting (`fnmatch`), API exponential backoff, and ghost file pruning. |
| ⚡ **Smart Deduplication** | Pre-calculates MD5 hashes of local files before querying Gemini. Identical, unmodified files bypass the API entirely to save your token quotas! |

---

## 🚀 Installation & Setup

We support two ways to run this server: **Zero-Install** (Recommended) or **Local Developer Clone**.
Make sure you have `uv` installed on your machine (`pip install uv`).

### Method 1: Zero-Install (Recommended)
You can point your AI assistant to run the server directly from GitHub without ever cloning the repository locally. `uvx` acts like `npx` for Python, downloading and caching the server in a secure ephemeral environment automatically!

## 🔑 Getting your Gemini API Key
To power the embedding model, you need a free API key from Google.
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Click **Create API key**.
3. Copy the key and use it in your client configurations below as `GEMINI_API_KEY`.

---

## 🔌 Client Connection Guides

### 🤖 Claude Code (CLI)
You can attach this server to the [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) CLI natively.
Run the following command in your terminal:

```bash
claude mcp add gemini-embedding-2-mcp \
  --env GEMINI_API_KEY="your-api-key-here" \
  -- uvx --from git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git gemini-embedding-2-mcp
```

### 🦋 Claude Desktop
Open your Claude Desktop config file (usually `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS) and add:
```json
{
  "mcpServers": {
    "gemini-embedding-2-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git",
        "gemini-embedding-2-mcp"
      ],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 💻 Cursor IDE
1. Go to **Settings** > **Features** > **MCP**
2. Click **+ Add new MCP server**
3. Choose **command** as the type.
4. Name: `gemini-embedding`
5. Command: `GEMINI_API_KEY="your-api-key" uvx --from git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git gemini-embedding-2-mcp`

### 🏄‍♂️ Windsurf (Cascade)
Open your `~/.codeium/windsurf/mcp_config.json` file and add:
```json
{
  "mcpServers": {
    "gemini-embedding-2-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git",
        "gemini-embedding-2-mcp"
      ],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### ⚡ Zed Editor
Open your `~/.config/zed/settings.json` and append the MCP server block:
```json
{
  "experimental.mcp": {
    "gemini-embedding-2-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git",
        "gemini-embedding-2-mcp"
      ],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 💻 VS Code (with Cline / RooCode)
Open `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` and append:
```json
{
  "mcpServers": {
    "gemini-embedding": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git",
        "gemini-embedding-2-mcp"
      ],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

---

### Method 2: Local Developer Clone

If you want to modify the source code:

```bash
# 1. Clone the repository
git clone https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git
cd gemini-embedding-2-mcp-server

# 2. Install dependencies
uv sync
```

*(If you use this method, you can add it directly to Claude Code CLI locally by running:)*
```bash
claude mcp add gemini-embedding-local --env GEMINI_API_KEY="your-api-key" -- uv --directory "$(pwd)" run gemini-embedding-2-mcp
```

---

## 🛠️ Exposed MCP Capabilities

Once connected, your AI assistant instantly gains the following tools:

### ⚙️ Tools
- `index_directory(path: str, ignore: list = None)`: Scan and formally embed a completely new local folder into the DB. Safely supports wildcard `ignore` patterns.
- `search_my_documents(query: str, limit: int)`: Run lighting-fast semantic cosine-similarity spatial search over the indexed database.
- `list_indexed_directories()`: See what paths the AI already knows about.
- `sync_indexed_directories()`: Automatically forces the DB to find new, updated, or recently deleted (ghost) files and cleans up vectors.
- `remove_directory_from_index(path: str)`: Clears a specific trajectory of vectors.

### 📊 Resources
- `gemini://database-stats`: Real-time observability! Exposes the exact scale of the vector segments inside ChromaDB directly to the assistant's context.

---

## 📚 Technical Documentation
- [Architecture Deep Dive](docs/architecture.md)
- [Ultimate Multimodality & PDF RAG](docs/multimodality.md)
- [Agentic Safety Guardrails](docs/agent-guardrails.md)

## 📜 License
MIT © Alaeddine Messadi
