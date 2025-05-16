"""
Tests for dashboard tools.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from supermetabase.tools.dashboard import get_dashboard, create_dashboard, get_dashboard_tab


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
        assert "dashcards" not in result_data
        assert "dashcard_count" in result_data
        assert result_data["is_single_tab"] is True
        
        # Verify the mock was called correctly
        client_mock.get_resource.assert_called_once_with("dashboard", 1)


@pytest.mark.asyncio
async def test_get_dashboard_with_tabs(mock_context, sample_dashboard):
    """Test dashboard retrieval with tabs."""
    # Create a dashboard with tabs
    dashboard_with_tabs = sample_dashboard.copy()
    dashboard_with_tabs["tabs"] = [
        {
            "id": 101,
            "dashboard_id": 1,
            "name": "Tab 1",
            "position": 0
        },
        {
            "id": 102,
            "dashboard_id": 1,
            "name": "Tab 2",
            "position": 1
        }
    ]
    dashboard_with_tabs["dashcards"] = [
        {
            "id": 1,
            "dashboard_id": 1,
            "dashboard_tab_id": 101,
            "size_x": 4,
            "size_y": 4,
            "row": 0,
            "col": 0
        },
        {
            "id": 2,
            "dashboard_id": 1,
            "dashboard_tab_id": 102,
            "size_x": 4,
            "size_y": 4,
            "row": 0,
            "col": 4
        }
    ]
    
    # Set up the mock
    client_mock = MagicMock()
    client_mock.get_resource = AsyncMock(return_value=dashboard_with_tabs)
    
    with patch("supermetabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_dashboard(id=1, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that the dashboard data is preserved
        assert result_data["id"] == 1
        assert result_data["name"] == "Test Dashboard"
        
        # Check that dashcards are not included
        assert "dashcards" not in result_data
        assert result_data["dashcard_count"] == 2
        
        # Check that tabs are included
        assert "tabs" in result_data
        assert len(result_data["tabs"]) == 2
        assert result_data["tabs"][0]["id"] == 101
        assert result_data["tabs"][1]["id"] == 102
        
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


@pytest.mark.asyncio
async def test_get_dashboard_tab_single_tab(mock_context, sample_dashboard, sample_card):
    """Test getting cards for a dashboard with a single tab."""
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
            "card": sample_card,
            "series": [sample_card]
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
        result = await get_dashboard_tab(dashboard_id=1, ctx=mock_context)  # No tab_id needed
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that the dashboard data is preserved
        assert result_data["dashboard_id"] == 1
        assert result_data["is_single_tab"] is True
        
        # Check that dashcards are present and processed
        assert "dashcards" in result_data
        assert len(result_data["dashcards"]) == 2
        assert result_data["dashcard_count"] == 2
        
        # Check that card objects have been simplified
        for dashcard in result_data["dashcards"]:
            # The card object should be null
            assert dashcard["card"] is None
            
            # A card_summary object should be present with id and name
            assert "card_summary" in dashcard
            assert dashcard["card_summary"]["id"] == sample_card["id"]
            assert dashcard["card_summary"]["name"] == sample_card["name"]
        
        # Verify the mock was called correctly
        client_mock.get_resource.assert_called_once_with("dashboard", 1)


@pytest.mark.asyncio
async def test_get_dashboard_tab_with_tabs(mock_context, sample_dashboard, sample_card):
    """Test getting cards for a specific tab in a multi-tab dashboard."""
    # Create a dashboard with tabs
    dashboard_with_tabs = sample_dashboard.copy()
    dashboard_with_tabs["tabs"] = [
        {
            "id": 101,
            "dashboard_id": 1,
            "name": "Tab 1",
            "position": 0
        },
        {
            "id": 102,
            "dashboard_id": 1,
            "name": "Tab 2",
            "position": 1
        }
    ]
    dashboard_with_tabs["dashcards"] = [
        {
            "id": 1,
            "dashboard_id": 1,
            "dashboard_tab_id": 101,
            "card_id": 1,
            "size_x": 4,
            "size_y": 4,
            "row": 0,
            "col": 0,
            "card": sample_card,
            "series": [sample_card]
        },
        {
            "id": 2,
            "dashboard_id": 1,
            "dashboard_tab_id": 102,
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
    client_mock.get_resource = AsyncMock(return_value=dashboard_with_tabs)
    
    with patch("supermetabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool for tab 101
        result = await get_dashboard_tab(dashboard_id=1, ctx=mock_context, tab_id=101)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that the dashboard data is preserved
        assert result_data["dashboard_id"] == 1
        assert "tab" in result_data
        assert result_data["tab"]["id"] == 101
        
        # Check that only cards from tab 101 are included
        assert "dashcards" in result_data
        assert len(result_data["dashcards"]) == 1
        assert result_data["dashcard_count"] == 1
        assert result_data["dashcards"][0]["dashboard_tab_id"] == 101
        
        # Verify the mock was called correctly
        client_mock.get_resource.assert_called_once_with("dashboard", 1)


@pytest.mark.asyncio
async def test_get_dashboard_tab_error_missing_tab_id(mock_context, sample_dashboard):
    """Test error when tab_id is required but not provided."""
    # Create a dashboard with tabs
    dashboard_with_tabs = sample_dashboard.copy()
    dashboard_with_tabs["tabs"] = [
        {"id": 101, "name": "Tab 1"},
        {"id": 102, "name": "Tab 2"}
    ]
    
    # Set up the mock
    client_mock = MagicMock()
    client_mock.get_resource = AsyncMock(return_value=dashboard_with_tabs)
    
    with patch("supermetabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool without tab_id
        result = await get_dashboard_tab(dashboard_id=1, ctx=mock_context)
        
        # Verify the error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        assert "success" in result_data
        assert result_data["success"] is False
        assert "error" in result_data
        assert result_data["error"]["error_type"] == "missing_tab_id"
        
        # Verify the mock was called correctly
        client_mock.get_resource.assert_called_once_with("dashboard", 1)


@pytest.mark.asyncio
async def test_get_dashboard_tab_error_invalid_tab_id(mock_context, sample_dashboard):
    """Test error when tab_id is provided but doesn't exist."""
    # Create a dashboard with tabs
    dashboard_with_tabs = sample_dashboard.copy()
    dashboard_with_tabs["tabs"] = [
        {"id": 101, "name": "Tab 1"},
        {"id": 102, "name": "Tab 2"}
    ]
    
    # Set up the mock
    client_mock = MagicMock()
    client_mock.get_resource = AsyncMock(return_value=dashboard_with_tabs)
    
    with patch("supermetabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool with non-existent tab_id
        result = await get_dashboard_tab(dashboard_id=1, ctx=mock_context, tab_id=999)
        
        # Verify the error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        assert "success" in result_data
        assert result_data["success"] is False
        assert "error" in result_data
        assert result_data["error"]["error_type"] == "tab_not_found"
        
        # Verify the mock was called correctly
        client_mock.get_resource.assert_called_once_with("dashboard", 1)


@pytest.mark.asyncio
async def test_get_dashboard_tab_error_invalid_tab_for_single_tab(mock_context, sample_dashboard):
    """Test error when tab_id is provided for a single-tab dashboard."""
    # Create a dashboard without tabs
    single_tab_dashboard = sample_dashboard.copy()
    # Ensure there's no 'tabs' field
    if "tabs" in single_tab_dashboard:
        del single_tab_dashboard["tabs"]
    
    # Set up the mock
    client_mock = MagicMock()
    client_mock.get_resource = AsyncMock(return_value=single_tab_dashboard)
    
    with patch("supermetabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool with tab_id for a single-tab dashboard
        result = await get_dashboard_tab(dashboard_id=1, ctx=mock_context, tab_id=101)
        
        # Verify the error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        assert "success" in result_data
        assert result_data["success"] is False
        assert "error" in result_data
        assert result_data["error"]["error_type"] == "invalid_tab"
        
        # Verify the mock was called correctly
        client_mock.get_resource.assert_called_once_with("dashboard", 1)
