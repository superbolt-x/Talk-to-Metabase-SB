"""
Tests for the run_dataset_query tool.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from supermetabase.tools.dataset import run_dataset_query


@pytest.mark.asyncio
async def test_run_native_dataset_query_success(mock_context):
    """Test executing a successful native dataset query."""
    # Sample query result
    query_result = {
        "data": {
            "rows": [
                ["Google", "2025-04-14T00:00:00Z", 18316.65625],
                ["Meta", "2025-03-10T00:00:00Z", 15587.970000000001]
            ],
            "cols": [
                {"name": "channel", "display_name": "channel", "base_type": "type/Text"},
                {"name": "date", "display_name": "date", "base_type": "type/Date"},
                {"name": "sum", "display_name": "sum", "base_type": "type/Float"}
            ],
            "native_form": {
                "query": "select channel, date, SUM(spend) from reporting.bariendo_blended WHERE date_granularity='week' GROUP BY 1,2"
            }
        },
        "status": "completed",
        "database_id": 195,
        "started_at": "2025-05-23T15:26:04.524227594Z",
        "running_time": 6242,
        "row_count": 2,
        "results_timezone": "UTC"
    }
    
    # Mock API response
    mock_response = (query_result, 200, None)
    
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(return_value=mock_response)
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    with patch("supermetabase.tools.dataset.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await run_dataset_query(
            database=195,
            native={"query": "select channel, date, SUM(spend) from reporting.bariendo_blended WHERE date_granularity='week' GROUP BY 1,2"},
            ctx=mock_context
        )
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check the response structure
        assert "data" in result_data
        assert "rows" in result_data["data"]
        assert len(result_data["data"]["rows"]) == 2
        assert "cols" in result_data["data"]
        assert "native_form" in result_data["data"]
        
        # Check other essential fields
        assert "status" in result_data
        assert result_data["status"] == "completed"
        assert "database_id" in result_data
        assert result_data["database_id"] == 195
        assert "started_at" in result_data
        assert "running_time" in result_data
        assert "row_count" in result_data
        assert result_data["row_count"] == 2
        assert "results_timezone" in result_data
        
        # Verify the mock was called correctly
        auth_mock.make_request.assert_called_once()
        call_args = auth_mock.make_request.call_args[0]
        assert call_args[0] == "POST"
        assert call_args[1] == "dataset"
        
        # Verify the query data was correctly formatted
        call_kwargs = auth_mock.make_request.call_args[1]
        assert "json" in call_kwargs
        assert call_kwargs["json"]["database"] == 195
        assert call_kwargs["json"]["type"] == "native"
        assert "query" in call_kwargs["json"]["native"]


@pytest.mark.asyncio
async def test_run_dataset_query_error(mock_context):
    """Test error handling for dataset query."""
    # Mock API error response with a SQL error
    error_response = {
        "database_id": 195,
        "started_at": "2025-05-23T15:36:30.405166542Z",
        "status": "failed",
        "error": "ERROR: column \"bariendo_blended.channel\" must appear in the GROUP BY clause or be used in an aggregate function",
        "error_type": "invalid-query",
        "stacktrace": ["driver.sql_jdbc.execute$execute_reducible_query$fn__89285$fn__89286.invoke(execute.clj:747)"]
    }
    
    # Mock API response
    mock_response = (error_response, 400, "ERROR: column \"bariendo_blended.channel\" must appear in the GROUP BY clause or be used in an aggregate function")
    
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(return_value=mock_response)
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    with patch("supermetabase.tools.dataset.get_metabase_client", return_value=client_mock):
        # Call the tool with a query that will cause an error
        result = await run_dataset_query(
            database=195,
            native={"query": "select channel, date, SUM(spend) from reporting.bariendo_blended WHERE date_granularity='week'"},
            ctx=mock_context
        )
        
        # Verify the error result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check error structure
        assert "success" in result_data
        assert result_data["success"] is False
        assert "error" in result_data
        assert result_data["error"]["error_type"] == "query_error"
        assert "must appear in the GROUP BY clause" in result_data["error"]["message"]
        
        # Verify the mock was called correctly
        auth_mock.make_request.assert_called_once()


@pytest.mark.asyncio
async def test_run_dataset_query_missing_parameters(mock_context):
    """Test parameter validation for dataset query."""
    # Set up the mock
    client_mock = MagicMock()
    
    with patch("supermetabase.tools.dataset.get_metabase_client", return_value=client_mock):
        # Call the tool without required parameters
        result = await run_dataset_query(
            database=195,
            native=None,  # Missing the native query object
            ctx=mock_context
        )
        
        # Verify the error result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check error structure
        assert "success" in result_data
        assert result_data["success"] is False
        assert "error" in result_data
        assert result_data["error"]["error_type"] == "missing_parameter"
        assert "Native query object is required" in result_data["error"]["message"]


@pytest.mark.asyncio
async def test_run_mbql_dataset_query(mock_context):
    """Test executing an MBQL dataset query."""
    # Sample query result for MBQL query
    query_result = {
        "data": {
            "rows": [
                ["Google", 85000.5],
                ["Meta", 65000.75]
            ],
            "cols": [
                {"name": "channel", "display_name": "Channel", "base_type": "type/Text"},
                {"name": "sum", "display_name": "Total Spend", "base_type": "type/Float"}
            ]
        },
        "status": "completed",
        "database_id": 195,
        "started_at": "2025-05-23T16:12:04.524227594Z",
        "running_time": 4587,
        "row_count": 2,
        "results_timezone": "UTC"
    }
    
    # Mock API response
    mock_response = (query_result, 200, None)
    
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(return_value=mock_response)
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    with patch("supermetabase.tools.dataset.get_metabase_client", return_value=client_mock):
        # Call the tool with an MBQL query
        result = await run_dataset_query(
            database=195,
            query={"source-table": 1234, "aggregation": [["sum", ["field", 5678, None]]], "breakout": [["field", 9012, None]]},
            type="query",
            ctx=mock_context
        )
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check the response structure
        assert "data" in result_data
        assert "rows" in result_data["data"]
        assert len(result_data["data"]["rows"]) == 2
        
        # Check essential fields
        assert "status" in result_data
        assert result_data["status"] == "completed"
        assert "row_count" in result_data
        assert result_data["row_count"] == 2
        
        # Verify the mock was called correctly
        auth_mock.make_request.assert_called_once()
        call_args = auth_mock.make_request.call_args[0]
        assert call_args[0] == "POST"
        assert call_args[1] == "dataset"
        
        # Verify the query data was correctly formatted
        call_kwargs = auth_mock.make_request.call_args[1]
        assert "json" in call_kwargs
        assert call_kwargs["json"]["database"] == 195
        assert call_kwargs["json"]["type"] == "query"
        assert "source-table" in call_kwargs["json"]["query"]
