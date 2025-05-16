"""
Tests for dashboard tools.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from supermetabase.tools.dashboard import get_dashboard, create_dashboard


@pytest.mark.asyncio
async def test_get_dashboard_success(mock_context, sample_dashboard):
    """Test successful dashboard retrieval."""
    # Set up the mock
    client_mock = MagicMock()
    client_mock.get_resource = AsyncMock(return_value=sample_dashboard)
    
    with patch("supermetabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_dashboard(id=1, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["id"] == 1
        assert result_data["name"] == "Test Dashboard"
        
        # Verify the mock was called correctly
        client_mock.get_resource.assert_called_once_with("dashboard", 1)


@pytest.mark.asyncio
async def test_get_dashboard_with_nested_cards(mock_context, sample_dashboard, sample_card):
    """Test dashboard retrieval with nested card data that gets simplified."""
    # Create a complex dashboard with nested cards
    complex_dashboard = sample_dashboard.copy()
    complex_dashboard["dashcards"] = [
        {
            "id": 1,
            "dashboard_id": 1,
            "card_id": 1,
            "size_x": 4,
            "size_y": 4,
            "row": 0,
            "col": 0,
            "card": sample_card,  # This is the nested card we expect to be simplified
            "series": [sample_card]  # This is a series card we expect to be simplified
        },
        {
            "id": 2,
            "dashboard_id": 1,
            "card_id": 2,
            "size_x": 4,
            "size_y": 4,
            "row": 0,
            "col": 4,
            "card": sample_card,
            "series": []
        }
    ]
    
    # Set up the mock
    client_mock = MagicMock()
    client_mock.get_resource = AsyncMock(return_value=complex_dashboard)
    
    with patch("supermetabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_dashboard(id=1, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that the dashboard data is preserved
        assert result_data["id"] == 1
        assert result_data["name"] == "Test Dashboard"
        
        # Check that dashcards are present
        assert "dashcards" in result_data
        assert len(result_data["dashcards"]) == 2
        
        # Check that card objects have been simplified
        for dashcard in result_data["dashcards"]:
            # The card object should be null
            assert dashcard["card"] is None
            
            # A card_summary object should be present with id and name
            assert "card_summary" in dashcard
            assert dashcard["card_summary"]["id"] == sample_card["id"]
            assert dashcard["card_summary"]["name"] == sample_card["name"]
        
        # Check that series have been simplified in the first dashcard
        assert "series_summary" in result_data["dashcards"][0]
        assert len(result_data["dashcards"][0]["series_summary"]) == 1
        assert result_data["dashcards"][0]["series_summary"][0]["id"] == sample_card["id"]
        assert result_data["dashcards"][0]["series_summary"][0]["name"] == sample_card["name"]
        assert result_data["dashcards"][0]["series"] == []
        
        # Verify the mock was called correctly
        client_mock.get_resource.assert_called_once_with("dashboard", 1)


@pytest.mark.asyncio
async def test_get_dashboard_error(mock_context):
    """Test dashboard retrieval with error."""
    # Set up the mock to raise an exception
    client_mock = MagicMock()
    client_mock.get_resource = AsyncMock(side_effect=ValueError("Test error"))
    
    with patch("supermetabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_dashboard(id=1, ctx=mock_context)
        
        # Verify the result is an error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["message"] == "Test error"
        assert result_data["error"]["error_type"] == "retrieval_error"


@pytest.mark.asyncio
async def test_create_dashboard_success(mock_context, sample_dashboard):
    """Test successful dashboard creation."""
    # Set up the mock
    client_mock = MagicMock()
    client_mock.create_resource = AsyncMock(return_value=sample_dashboard)
    
    with patch("supermetabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await create_dashboard(
            name="Test Dashboard",
            ctx=mock_context,
            description="A test dashboard",
            collection_id=1
        )
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["id"] == 1
        assert result_data["name"] == "Test Dashboard"
        
        # Verify the mock was called correctly
        client_mock.create_resource.assert_called_once()
        # Get the first positional argument (resource_type)
        assert client_mock.create_resource.call_args[0][0] == "dashboard"
        # Get the dashboard_data argument
        dashboard_data = client_mock.create_resource.call_args[0][1]
        assert dashboard_data["name"] == "Test Dashboard"
        assert dashboard_data["description"] == "A test dashboard"
        assert dashboard_data["collection_id"] == 1
