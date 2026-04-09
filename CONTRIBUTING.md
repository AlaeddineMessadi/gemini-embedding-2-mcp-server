# Contributing to Gemini Embedding 2 MCP

Thank you for your interest in contributing! This project is an open-source initiative to bring powerful Gemini semantic search to local documents via MCP.

## Getting Started

1. Fork the repository
2. Install [`uv`](https://github.com/astral-sh/uv)
3. Set up your local environment:
   ```bash
   uv sync
   ```
4. Create a new branch: `git checkout -b feature/your-feature-name`
5. Make your changes and write descriptive commit messages.
6. Push and submit a Pull Request!

## Local Quality Checks

Before opening a pull request, run:

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

If your change affects packaging or deployment, also verify:

```bash
docker build -t gemini-embedding-2-mcp-server:test .
```

## Release and Maintenance Model

- `main` should stay releasable
- Pull requests should include tests for behavior changes
- User-facing behavior changes should update the README or technical docs
- Tags starting with `v` are intended to drive automated release packaging

## Architecture
The server relies on the new `gemini-embedding-2-preview` model. If you are adding new document parsers (e.g., proper PPTX support), please ensure they output clean Markdown-like strings for better embedding quality.
