import os
import chromadb
from typing import List, Dict, Any

# default to user's home directory for DB persistence
DEFAULT_DB_PATH = os.path.expanduser("~/.gemini_mcp_db")
COLLECTION_NAME = "documents"


class ChromaStore:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        # PersistentClient writes data to disk automatically
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Adds text chunks and their corresponding embeddings to ChromaDB.
        `chunks` should be a list of dicts: {"text": str, "metadata": dict}
        """
        if not chunks or not embeddings:
            return

        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings.")

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            # Create a unique ID combining source and chunk_index
            source = chunk["metadata"]["source"]
            chunk_idx = chunk["metadata"]["chunk_index"]
            doc_id = f"{source}::{chunk_idx}"

            ids.append(doc_id)
            # Add a fallback text for images so they don't break chromadb requirements
            documents.append(
                chunk.get(
                    "text", f"[{chunk['metadata'].get('type', 'document')}] {source}"
                )
            )
            metadatas.append(chunk["metadata"])

        # We use upsert so we overwrite if it already exists (updating)
        self.collection.upsert(
            ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
        )

    def delete_directory(self, directory_path: str) -> int:
        """
        Deletes all chunks that originated from within a specific directory.
        Returns the number of deleted vectors.
        """
        # We have to fetch all sources, find matching ones, and delete by ID since Chroma
        # metadata filtering on string startswith is limited.
        data = self.collection.get(include=["metadatas"])
        if not data or not data["metadatas"]:
            return 0

        ids_to_delete = []
        for doc_id, meta in zip(data["ids"], data["metadatas"]):
            if meta and "source" in meta and meta["source"].startswith(directory_path):
                ids_to_delete.append(doc_id)

        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)

        return len(ids_to_delete)

    def delete_file(self, file_path: str) -> int:
        """
        Deletes all chunks exactly matching a specific source file path.
        """
        data = self.collection.get(include=["metadatas"])
        if not data or not data["metadatas"]:
            return 0

        ids_to_delete = []
        for doc_id, meta in zip(data["ids"], data["metadatas"]):
            if meta and meta.get("source") == file_path:
                ids_to_delete.append(doc_id)

        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)

        return len(ids_to_delete)

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filters: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Queries ChromaDB using the query vector and returns the top matches.
        """
        if not query_embedding:
            return []

        total = self.collection.count()
        if total == 0:
            return []

        candidate_count = min(max(n_results * 10, 25), total)

        results = self.collection.query(
            query_embeddings=[query_embedding], n_results=candidate_count
        )

        matches = []
        # chromadb returns lists of lists because of batch querying
        if results and results["documents"] and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = (
                results["distances"][0]
                if "distances" in results and results["distances"]
                else [0] * len(docs)
            )

            for doc, meta, dist in zip(docs, metas, distances):
                if self._matches_filters(meta or {}, filters):
                    matches.append({"text": doc, "metadata": meta, "distance": dist})

        return matches[:n_results]

    def list_indexed_sources(self) -> List[str]:
        """Returns a list of unique 'source' files indexed in the database."""
        # This gets expensive for huge databases, but for local docs it's fine.
        data = self.collection.get(include=["metadatas"])
        if not data or not data["metadatas"]:
            return []

        sources = set()
        for meta in data["metadatas"]:
            if meta and "source" in meta:
                sources.add(meta["source"])

        return sorted(list(sources))

    def list_indexed_directories(self) -> List[str]:
        """Returns unique indexed parent directories."""
        directories = {
            os.path.dirname(source) for source in self.list_indexed_sources()
        }
        return sorted(directory for directory in directories if directory)

    def get_source_entries(self, source: str) -> List[Dict[str, Any]]:
        """Returns all stored entries for a given source file sorted by location."""
        results = self.collection.get(
            where={"source": source}, include=["documents", "metadatas"]
        )
        if not results or not results["metadatas"]:
            return []

        entries = []
        for doc, meta in zip(results["documents"], results["metadatas"]):
            entries.append({"text": doc, "metadata": meta})

        return sorted(
            entries,
            key=lambda entry: (
                entry["metadata"].get("page_number")
                if entry["metadata"].get("page_number") is not None
                else entry["metadata"].get("chunk_index", 0),
                entry["metadata"].get("chunk_index", 0),
            ),
        )

    def get_indexed_file_hashes(self, directory_path: str = "") -> Dict[str, str]:
        """
        Returns a mapping of {source_file_path: file_hash} for all indexed files
        that start with the given directory_path.
        """
        data = self.collection.get(include=["metadatas"])
        if not data or not data["metadatas"]:
            return {}

        file_hashes = {}
        for meta in data["metadatas"]:
            if meta and "source" in meta and "file_hash" in meta:
                source = meta["source"]
                if not directory_path or source.startswith(directory_path):
                    # We might encounter multiple chunks for the same source,
                    # but they should all have the same file_hash.
                    if source not in file_hashes:
                        file_hashes[source] = meta["file_hash"]

        return file_hashes

    @staticmethod
    def _matches_filters(
        metadata: Dict[str, Any], filters: Dict[str, Any] | None = None
    ) -> bool:
        if not filters:
            return True

        scope = filters.get("scope")
        if scope and not metadata.get("source", "").startswith(scope):
            return False

        path_prefix = filters.get("path_prefix")
        if path_prefix and not metadata.get("source", "").startswith(path_prefix):
            return False

        types = filters.get("types")
        if types and metadata.get("type") not in set(types):
            return False

        extensions = filters.get("extensions")
        if extensions:
            normalized = {
                extension if extension.startswith(".") else f".{extension}"
                for extension in extensions
            }
            if metadata.get("extension") not in normalized:
                return False

        modalities = filters.get("modalities")
        if modalities and metadata.get("modality") not in set(modalities):
            return False

        return True
