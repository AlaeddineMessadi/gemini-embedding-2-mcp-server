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

## 3. Preview Before Indexing
Before running a full scan, an agent can call `preview_directory()` to inspect:
- how many files are eligible
- what modalities will be indexed
- what gets skipped
- why it gets skipped

This lowers the risk of large or noisy scans without requiring a user to manually configure the server first.

## 4. Ghost File Purging
When the `sync_indexed_directories` tool is called, it first performs a silent integrity check on `ChromaDB`. It checks your disk to see if any previously indexed files have been permanently deleted. If it finds missing files, it strictly purges their stale vectors from the database to prevent hallucinations.

## 5. API Exponential Backoff
When indexing huge folders, there is a realistic chance of hitting Google API Quota Rate Limits (`HTTP 429 Too Many Requests`). Instead of violently crashing the MCP Server midway through a 5-minute index, the server catches the exception, calculates an exponential back-off (`2^attempt` seconds), and retries the batch gracefully in the background.

## 6. Root Directory Suicide Blocks
The server restricts hard-limits of `2,000` files per directory tool-call to prevent memory exhaustion, and explicitly throws an error if the agent attempts to index root operating system folders (e.g., `/`, `/Users`, `C:\`).

## 7. Smart Deduplication (Token Saver)
When an agent or user attempts to re-index an existing directory, the server does not blindly re-read every file and hit the Gemini API. Instead, it computes an MD5 hash of the local file and compares it to the tracked metadata in the ChromaDB vector database. Unmodified files completely bypass the embedding pipeline, saving massive amounts of API tokens and quotas during subsequent folder syncs. Overwritten files are dynamically purged from the database and re-embedded seamlessly.

## 8. Compact Controls Instead of Heavy Config
The server is designed to be safe by default. Rather than requiring a large configuration file up front, it keeps the public control surface compact:
- `ignore`
- `scope`
- `path_prefix`
- `types`
- `extensions`
- `modalities`

That gives agents enough precision to get what they want without turning setup into an operations task.
