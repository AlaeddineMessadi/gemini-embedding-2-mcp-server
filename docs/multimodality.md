# Ultimate Multimodality

Unlike previous generation text-only embeddings, the `gemini-embedding-2-preview` model accepts **any type of media** up to 8,192 tokens. This MCP server is uniquely designed to act as an abstraction layer to fully unleash this capability inside your local filesystem.

## 1. Native Media Embeddings
When the server scans a directory via `index_directory`, it doesn't just read code or `.txt` files. It natively loads:
- **Images**: `.jpg`, `.jpeg`, `.png`, `.webp`
- **Video**: `.mp4`
- **Audio**: `.mp3`, `.wav`, `.aiff`, `.aac`

Instead of trying to extract text from a video, the server sends the **raw binary file** (`types.Part.from_bytes`) directly to the Gemini Embedding 2 model. Gemini literally "watches" the video or "listens" to the audio clip and generates a semantic float tensor representing its meaning.

When an LLM (Claude) queries your database, it can retrieve the path to that specific `.mp4` based entirely on the visual or auditory concepts contained within it!

## 2. Visual PDF Hybrid RAG
Perhaps the most groundbreaking feature of this server is how it handles `.pdf` documents.

Traditionally, RAG architectures use libraries like `PyMuPDF` or `pdf2text` to strip raw text strings out of documents. This destroys formatting, strips out embedded tables, drops charts, and ignores layout.

### Our Solution
1. **The Photograph**: The server iterates through every single page of a PDF and renders it as a high-definition `150 DPI` PNG Image.
2. **The Embedding**: That image is sent to Gemini Embedding 2. Gemini natively "looks" at the page layout, comprehends the charts, reads the formulas, and generates a flawless semantic spatial vector.
3. **The Hybrid Storage**: In parallel, we *also* extract the raw text, but we only use it as the fallback metadata for ChromaDB!

This means when Claude searches, it mathematically matches the query against the *visually mapped vector*, but is handed the raw text so it can easily read, cite, and quote the PDF!
