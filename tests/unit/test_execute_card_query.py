"""
Tests for the execute_card_query tool.
"""

import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from supermetabase.tools.dashboard import execute_card_query


@pytest.mark.asyncio
async def test_execute_standalone_card_query(mock_context):
    """Test executing a standalone card query."""
    # Sample query result
    query_result = {
        "data": {
            "rows": [
                ["Row 1 Value 1", "Row 1 Value 2"],
                ["Row 2 Value 1", "Row 2 Value 2"]
            ],
            "cols": [
                {"name": "Column 1", "display_name": "Column 1", "base_type": "type/Text"},
                {"name": "Column 2", "display_name": "Column 2", "base_type": "type/Text"}
            ],
            "native_form": {
                "query": "SELECT * FROM table LIMIT 2"
            }
        },
        "status": "completed",
        "json_query": {
            "database": 1,
            "type": "query",
            "query": {
                "source-table": 1,
                "limit": 2
            }
        }
    }
    
    # Mock API response
    mock_response = (query_result, 200, None)
    
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(return_value=mock_response)
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    with patch("supermetabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await execute_card_query(card_id=123, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check the response structure
        assert "data" in result_data
        assert "rows" in result_data["data"]
        assert len(result_data["data"]["rows"]) == 2
        
        # Check that metadata was added
        assert "metadata" in result_data
        assert "execution_context" in result_data["metadata"]
        assert result_data["metadata"]["execution_context"]["card_id"] == 123
        assert result_data["metadata"]["execution_context"]["query_type"] == "standalone_card"
        assert "row_count" in result_data["metadata"]
        assert result_data["metadata"]["row_count"] == 2
        
        # Verify the mock was called correctly
        auth_mock.make_request.assert_called_once()
        call_args = auth_mock.make_request.call_args[0]
        assert call_args[0] == "POST"
        assert call_args[1] == "card/123/query"


@pytest.mark.asyncio
async def test_execute_dashboard_card_query(mock_context):
    """Test executing a card query in a dashboard context."""
    # Sample query result
    query_result = {
        "data": {
            "rows": [
                ["Row 1 Value 1", "Row 1 Value 2"],
                ["Row 2 Value 1", "Row 2 Value 2"],
                ["Row 3 Value 1", "Row 3 Value 2"]
            ],
            "cols": [
                {"name": "Column 1", "display_name": "Column 1", "base_type": "type/Text"},
                {"name": "Column 2", "display_name": "Column 2", "base_type": "type/Text"}
            ]
        },
        "status": "completed"
    }
    
    # Mock API response
    mock_response = (query_result, 200, None)
    
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(return_value=mock_response)
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    with patch("supermetabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await execute_card_query(
            card_id=123,
            dashboard_id=456,
            dashcard_id=789,
            parameters=[{"id": "param1", "value": "value1"}],
            ctx=mock_context
        )
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check the response structure
        assert "data" in result_data
        assert "rows" in result_data["data"]
        assert len(result_data["data"]["rows"]) == 3
        
        # Check that metadata was added
        assert "metadata" in result_data
        assert "execution_context" in result_data["metadata"]
        assert result_data["metadata"]["execution_context"]["card_id"] == 123
        assert result_data["metadata"]["execution_context"]["dashboard_id"] == 456
        assert result_data["metadata"]["execution_context"]["dashcard_id"] == 789
        assert result_data["metadata"]["execution_context"]["query_type"] == "dashboard_card"
        assert result_data["metadata"]["row_count"] == 3
        
        # Verify the mock was called correctly
        auth_mock.make_request.assert_called_once()
        call_args = auth_mock.make_request.call_args[0]
        assert call_args[0] == "POST"
        assert call_args[1] == "dashboard/456/dashcard/789/card/123/query"
        
        # Check that the parameters were passed correctly
        call_kwargs = auth_mock.make_request.call_args[1]
        assert "json" in call_kwargs
        assert "parameters" in call_kwargs["json"]
        assert call_kwargs["json"]["parameters"] == [{"id": "param1", "value": "value1"}]
        assert "dashboard_load_id" in call_kwargs["json"]


@pytest.mark.asyncio
async def test_execute_card_query_missing_parameter(mock_context):
    """Test error handling when dashboard_id is provided but dashcard_id is missing."""
    # Set up the mock
    client_mock = MagicMock()
    
    with patch("supermetabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool with dashboard_id but no dashcard_id
        result = await execute_card_query(
            card_id=123,
            dashboard_id=456,  # Provide dashboard_id
            dashcard_id=None,  # But no dashcard_id
            ctx=mock_context
        )
        
        # Verify the error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        assert "success" in result_data
        assert result_data["success"] is False
        assert "error" in result_data
        assert result_data["error"]["error_type"] == "missing_parameter"
        assert "dashcard_id is required" in result_data["error"]["message"]


@pytest.mark.asyncio
async def test_execute_card_query_api_error(mock_context):
    """Test handling of API errors."""
    # Mock API error response
    mock_response = (None, 404, "Card not found")
    
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(return_value=mock_response)
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    with patch("supermetabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await execute_card_query(card_id=999, ctx=mock_context)
        
        # Verify the error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        assert "success" in result_data
        assert result_data["success"] is False
        assert "error" in result_data
        assert result_data["error"]["error_type"] == "query_error"
        assert result_data["error"]["message"] == "Card not found"
        
        # Verify the mock was called correctly
        auth_mock.make_request.assert_called_once()
