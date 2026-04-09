<div align="center">
  <img src="assets/banner.svg" alt="Gemini Embedding 2 MCP Server Banner" />

  <p align="center">
    <strong>A multimodal local memory MCP for AI agents powered by Gemini Embedding 2.</strong>
  </p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
  [![MCP](https://img.shields.io/badge/MCP-Compatible-8A2BE2.svg)](https://modelcontextprotocol.io/)
  [![CI](https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server/actions/workflows/ci.yml)
</div>

---

Connect your local documents, code, PDFs, images, audio, and video directly to **Claude**, **Cursor**, or **VS Code** using Google's `gemini-embedding-2-preview` model and a strictly local **ChromaDB** vector database.

Unlike text-only local RAG tools, this server keeps one local memory layer across text, visual PDF pages, images, audio, and video, then returns exact file paths and page or chunk context back to your agent.

## Why This Is Different

- **One embedding space across modalities**: Search code, PDFs, images, audio, and video from the same memory layer.
- **Local-first persistence**: Your index stays in `~/.gemini_mcp_db`, not in a hosted vector database.
- **Agent-friendly retrieval**: Search results include exact paths, types, modalities, and page-aware context.
- **Zero-config by default**: The server uses built-in guardrails and sensible indexing defaults so most users do not need a config file.

## What You Can Ask

- `Find the PDF page that explains our design tokens.`
- `Search my image library for screenshots of dashboards with dark sidebars.`
- `Find the audio or video clip where we talked about pricing changes.`
- `Search only my work docs folder for onboarding notes about incident response.`
- `Give me the surrounding context for result 2 so I can cite the original file correctly.`

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| 🧠 **Unified Multimodal Search** | Stores text, visual PDF pages, images, audio, and video in one local semantic memory so a single query can retrieve across modalities. |
| 📄 **Visual PDF Retrieval** | Renders PDFs page-by-page as images for Gemini Embedding 2 while retaining extracted text for agent-readable citations and context. |
| 🎯 **Precision Retrieval Controls** | Supports compact filters for scope, path prefix, type, extension, and modality so agents can search precisely without heavy configuration. |
| 👀 **Preview Before Indexing** | `preview_directory()` shows what will be indexed, grouped by modality and skip reason, before the scan runs. |
| 🧾 **Context-Aware Results** | `get_result_context()` returns neighboring chunks or pages so agents can inspect exact source material after search. |
| 🛡️ **Local Privacy + Guardrails** | Uses a local ChromaDB store, skips junk folders by default, blocks dangerous root scans, and handles deduplication and ghost-file cleanup automatically. |

---

## 🚀 Installation & Setup

We support two ways to run this server: **Zero-Install** (Recommended) or **Local Developer Clone**.
Make sure you have `uv` installed on your machine (`pip install uv`).

### Method 1: Zero-Install (Recommended)
You can point your AI assistant to run the server directly from GitHub without ever cloning the repository locally. `uvx` acts like `npx` for Python, downloading and caching the server in a secure ephemeral environment automatically.

PyPI is configured as the long-term stable distribution channel for tagged releases. Until the first PyPI publish completes, use the pinned Git release-tag install below.

For a **stable install**, pin to a release tag:

```bash
uvx --from git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git@<release-tag> gemini-embedding-2-mcp
```

Example:

```bash
uvx --from git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git@v1.2.1 gemini-embedding-2-mcp
```

For an **edge install**, omit the tag and track the latest `main` branch state.

Once PyPI publishing is live, the stable install command becomes:

```bash
uvx gemini-embedding-2-mcp-server
```

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
  -- uvx --from git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git@v1.2.1 gemini-embedding-2-mcp
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
        "git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git@v1.2.1",
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
5. Command: `GEMINI_API_KEY="your-api-key" uvx --from git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git@v1.2.1 gemini-embedding-2-mcp`

### 🏄‍♂️ Windsurf (Cascade)
Open your `~/.codeium/windsurf/mcp_config.json` file and add:
```json
{
  "mcpServers": {
    "gemini-embedding-2-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git@v1.2.1",
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
        "git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git@v1.2.1",
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
        "git+https://github.com/AlaeddineMessadi/gemini-embedding-2-mcp-server.git@v1.2.1",
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

### Method 3: Docker

If you need a containerized MCP server for registry validation or deployment, build and run the included image:

```bash
docker build -t gemini-embedding-2-mcp-server .
docker run --rm -i \
  -e GEMINI_API_KEY="your-api-key-here" \
  -v "$HOME/.gemini_mcp_db:/root/.gemini_mcp_db" \
  gemini-embedding-2-mcp-server
```

The container communicates over standard I/O like any other local MCP server and persists ChromaDB data in the mounted volume.

---

## 🛠️ Exposed MCP Capabilities

Once connected, your AI assistant instantly gains the following tools:

### ⚙️ Tools
- `index_directory(path: str, ignore: list = None)`: Scan and formally embed a completely new local folder into the DB. Safely supports wildcard `ignore` patterns.
- `preview_directory(path: str, ignore: list = None)`: Dry-run a scan and see what would be indexed, grouped by modality and skip reason.
- `search_my_documents(query: str, limit: int, scope: str = None, types: list[str] = None, path_prefix: str = None, extensions: list[str] = None, modalities: list[str] = None)`: Run semantic search with compact retrieval filters.
- `get_result_context(source: str, locator: str = None, window: int = 1)`: Fetch nearby chunk or page context for a previously indexed result.
- `list_indexed_directories()`: See which directory roots the AI already knows about.
- `sync_indexed_directories()`: Automatically forces the DB to find new, updated, or recently deleted (ghost) files and cleans up vectors.
- `remove_directory_from_index(path: str)`: Clears a specific trajectory of vectors.

### 🔎 Precision Filters

The main search tool stays simple by default, but supports a few high-value filters when you need exactness:

- `scope`: Limit matches to a broad directory scope such as `/Users/me/work`
- `path_prefix`: Limit matches to a more exact path prefix
- `types`: Restrict by stored item type such as `text` or `pdf_visual_page`
- `extensions`: Restrict by file extension such as `.pdf` or `.md`
- `modalities`: Restrict by modality such as `text`, `pdf`, `image`, `audio`, or `video`

### 📊 Resources
- `gemini://database-stats`: Real-time observability! Exposes the exact scale of the vector segments inside ChromaDB directly to the assistant's context.

---

## 📚 Technical Documentation
- [Architecture Deep Dive](docs/architecture.md)
- [Ultimate Multimodality & PDF RAG](docs/multimodality.md)
- [Agentic Safety Guardrails](docs/agent-guardrails.md)
- [Use Cases](docs/use-cases.md)
- [Result Model](docs/result-model.md)
- [Releasing](docs/releasing.md)

## 📜 License
MIT © Alaeddine Messadi
