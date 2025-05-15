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
