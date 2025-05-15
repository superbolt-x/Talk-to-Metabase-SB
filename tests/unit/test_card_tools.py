"""
Tests for card tools.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from supermetabase.tools.card import get_card


@pytest.mark.asyncio
async def test_get_card_success(mock_context, sample_card):
    """Test successful card retrieval."""
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(return_value=(sample_card, 200, None))
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    with patch("supermetabase.tools.card.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_card(id=1, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["id"] == 1
        assert result_data["name"] == "Test Card"
        
        # Verify the mock was called correctly
        auth_mock.make_request.assert_called_once_with("GET", "card/1", params={})


@pytest.mark.asyncio
async def test_get_card_with_params(mock_context, sample_card):
    """Test card retrieval with query parameters."""
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(return_value=(sample_card, 200, None))
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    with patch("supermetabase.tools.card.get_metabase_client", return_value=client_mock):
        # Call the tool with parameters
        result = await get_card(
            id=1, 
            ctx=mock_context,
            ignore_view=True,
            context="collection"
        )
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["id"] == 1
        
        # Verify the mock was called with the correct parameters
        auth_mock.make_request.assert_called_once_with(
            "GET", 
            "card/1", 
            params={"ignore_view": "true", "context": "collection"}
        )


@pytest.mark.asyncio
async def test_get_card_error(mock_context):
    """Test card retrieval with error."""
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(
        return_value=({"error": "Not found"}, 404, "Card not found")
    )
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    with patch("supermetabase.tools.card.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_card(id=999, ctx=mock_context)
        
        # Verify the result is an error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["message"] == "Card not found"
        assert result_data["error"]["error_type"] == "retrieval_error"
