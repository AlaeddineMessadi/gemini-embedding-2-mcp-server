# Enterprise Agentic Guardrails

This MCP server was built explicitly for **autonomous AI agents** (like Claude 3.5 Sonnet on Claude Desktop). When given unlimited access to a local `/Users/` filesystem, an agent might accidentally request catastrophic recursive scans.

To ensure extreme reliability and host machine safety, the server implements multiple "invisible" guardrails:

## 1. The Junk Filter (`IGNORE_DIRS`)
If Claude decides to recursively index your `~/Documents/Projects` folder, it will likely hit a `node_modules` directory containing 100,000 cached library files. This would waste API limits and pollute the ChromaDB index. 
- The server natively skips hidden directories (`.*`) and automatically ignores heavy build folders (`node_modules`, `venv`, `build`, `dist`, `__pycache__`, `out`, `target`).

## 2. Dynamic Blacklisting (`fnmatch`)
If a user or agent specifically wants to ignore certain files during a scan, they can use the `ignore` parameter in the `index_directory` tool:
- Example: `index_directory("/app", ignore=["*.log", "drafts", "secrets.*"])`
- This uses Python's `fnmatch` wildcard testing at the filesystem ingestion level for maximum performance.

## 3. Ghost File Purging
When the `sync_indexed_directories` tool is called, it first performs a silent integrity check on `ChromaDB`. It checks your disk to see if any previously indexed files have been permanently deleted. If it finds missing files, it strictly purges their stale vectors from the database to prevent hallucinations.

## 4. API Exponential Backoff
When indexing huge folders, there is a realistic chance of hitting Google API Quota Rate Limits (`HTTP 429 Too Many Requests`). Instead of violently crashing the MCP Server midway through a 5-minute index, the server catches the exception, calculates an exponential back-off (`2^attempt` seconds), and retries the batch gracefully in the background.

## 5. Root Directory Suicide Blocks
The server restricts hard-limits of `2,000` files per directory tool-call to prevent memory exhaustion, and explicitly throws an error if the agent attempts to index root operating system folders (e.g., `/`, `/Users`, `C:\`).
