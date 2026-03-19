from unittest.mock import MagicMock
import pytest
from gemini_mcp.embeddings.gemini import GeminiEmbeddingClient

def test_embed_query(mocker):
    # Mock the underlying google.genai.Client
    mock_client = MagicMock()
    
    # Mock the specific returned embeddings payload
    mock_response = MagicMock()
    mock_emb = MagicMock()
    mock_emb.values = [0.1, 0.2, 0.3]
    mock_response.embeddings = [mock_emb]
    
    # Apply the mock deep down
    mock_embed_content = MagicMock(return_value=mock_response)
    mock_client.models.embed_content = mock_embed_content
    
    # Patch the google SDK constructor to return our mock
    mocker.patch("gemini_mcp.embeddings.gemini.genai.Client", return_value=mock_client)
    
    client = GeminiEmbeddingClient(api_key="fake-key")
    result = client.embed_query("Test query")
    
    assert result == [0.1, 0.2, 0.3]
    mock_embed_content.assert_called_once()
    
    # Validate task_type was correct
    call_args = mock_embed_content.call_args[1]
    assert call_args["config"].task_type == "RETRIEVAL_QUERY"
