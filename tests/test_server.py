import pytest

from gemini_mcp import server


class FakeEmbedder:
    def embed_query(self, query):
        assert query == "design system"
        return [0.1, 0.2, 0.3]


class FakeDB:
    def query(self, query_embedding, n_results=5, filters=None):
        assert query_embedding == [0.1, 0.2, 0.3]
        assert n_results == 2
        assert filters == {
            "scope": "/vault/work",
            "types": ["pdf_visual_page"],
            "path_prefix": "/vault/work/docs",
            "extensions": [".pdf"],
            "modalities": ["pdf"],
        }
        return [
            {
                "text": "--- Page 3 from handbook.pdf ---\nDesign tokens and layout.",
                "metadata": {
                    "source": "/vault/work/docs/handbook.pdf",
                    "filename": "handbook.pdf",
                    "extension": ".pdf",
                    "type": "pdf_visual_page",
                    "modality": "pdf",
                    "page_number": 3,
                },
                "distance": 0.111,
            }
        ]

    def list_indexed_sources(self):
        return [
            "/vault/work/docs/handbook.pdf",
            "/vault/work/docs/notes.md",
            "/vault/personal/photos/reference.png",
        ]

    def get_source_entries(self, source):
        assert source == "/vault/work/docs/notes.md"
        return [
            {
                "text": "intro",
                "metadata": {"chunk_index": 0, "source": source, "type": "text"},
            },
            {
                "text": "design tokens",
                "metadata": {"chunk_index": 1, "source": source, "type": "text"},
            },
            {
                "text": "spacing system",
                "metadata": {"chunk_index": 2, "source": source, "type": "text"},
            },
        ]

    def list_indexed_directories(self):
        return ["/vault/personal/photos", "/vault/work/docs"]


@pytest.mark.asyncio
async def test_search_my_documents_supports_filters_and_rich_results(mocker):
    mocker.patch.object(server, "get_db", return_value=FakeDB())
    mocker.patch.object(server, "get_embedder", return_value=FakeEmbedder())

    result = await server.search_my_documents(
        "design system",
        limit=2,
        scope="/vault/work",
        types=["pdf_visual_page"],
        path_prefix="/vault/work/docs",
        extensions=[".pdf"],
        modalities=["pdf"],
    )

    assert "Found 1 relevant result" in result
    assert "Type: pdf_visual_page" in result
    assert "Modality: pdf" in result
    assert "Page: 3" in result
    assert "/vault/work/docs/handbook.pdf" in result


@pytest.mark.asyncio
async def test_get_result_context_returns_neighboring_chunks(mocker):
    mocker.patch.object(server, "get_db", return_value=FakeDB())

    result = await server.get_result_context(
        "/vault/work/docs/notes.md", locator="chunk:1", window=1
    )

    assert "Context for /vault/work/docs/notes.md" in result
    assert "Chunk 0" in result
    assert "Chunk 1" in result
    assert "Chunk 2" in result
    assert "design tokens" in result


@pytest.mark.asyncio
async def test_list_indexed_directories_returns_unique_directories(mocker):
    mocker.patch.object(server, "get_db", return_value=FakeDB())

    result = await server.list_indexed_directories()

    assert "/vault/work/docs" in result
    assert "/vault/personal/photos" in result
    assert "handbook.pdf" not in result
