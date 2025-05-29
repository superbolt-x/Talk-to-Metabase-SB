"""
Tests for the database metadata tool.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from talk_to_metabase.tools.database import get_database_metadata


@pytest.fixture
def sample_metadata():
    """Sample database metadata response from Metabase API."""
    return {
        "id": 130,
        "name": "Ask Tia",
        "engine": "redshift",
        "timezone": "GMT",
        "features": [
            "describe-fks",
            "full-join",
            "window-functions/cumulative",
            "test/dynamic-dataset-loading",
            "describe-fields",
            "basic-aggregations"
        ],
        "tables": [
            {
                "description": None,
                "entity_type": "entity/UserTable",
                "schema": "facebook_raw",
                "name": "account_history",
                "fields": [],
                "active": True,
                "id": 34320,
                "db_id": 130,
                "visibility_type": None,
                "field_order": "database",
                "display_name": "Account History",
                "initial_sync_status": "complete"
            },
            {
                "description": None,
                "entity_type": "entity/UserTable",
                "schema": "googleads_raw",
                "name": "account_history",
                "fields": [],
                "active": True,
                "id": 34422,
                "db_id": 130,
                "visibility_type": None,
                "field_order": "database",
                "display_name": "Account History",
                "initial_sync_status": "complete"
            },
            {
                "description": None,
                "entity_type": "entity/UserTable",
                "schema": "googleads_raw",
                "name": "account_hourly_stats",
                "fields": [],
                "active": True,
                "id": 34322,
                "db_id": 130,
                "visibility_type": None,
                "field_order": "database",
                "display_name": "Account Hourly Stats",
                "initial_sync_status": "complete"
            },
            {
                "description": None,
                "entity_type": "entity/UserTable",
                "schema": "googleads_raw",
                "name": "account_stats",
                "fields": [],
                "active": True,
                "id": 34386,
                "db_id": 130,
                "visibility_type": None,
                "field_order": "database",
                "display_name": "Account Stats",
                "initial_sync_status": "complete"
            },
            {
                "description": None,
                "entity_type": "entity/GenericTable",
                "schema": "facebook_raw",
                "name": "ad_campaign_issues_info",
                "fields": [],
                "active": True,
                "id": 34429,
                "db_id": 130,
                "visibility_type": None,
                "field_order": "database",
                "display_name": "Ad Campaign Issues Info",
                "initial_sync_status": "complete"
            }
        ]
    }


@pytest.fixture
def expected_simplified_output():
    """Expected simplified output from the get_database_metadata tool."""
    return {
        "database": {
            "id": 130,
            "name": "Ask Tia",
            "engine": "redshift",
            "timezone": "GMT"
        },
        "schemas": [
            {
                "name": "facebook_raw",
                "tables": [
                    {
                        "id": 34320,
                        "name": "account_history",
                        "entity_type": "entity/UserTable"
                    },
                    {
                        "id": 34429,
                        "name": "ad_campaign_issues_info",
                        "entity_type": "entity/GenericTable"
                    }
                ]
            },
            {
                "name": "googleads_raw",
                "tables": [
                    {
                        "id": 34422,
                        "name": "account_history",
                        "entity_type": "entity/UserTable"
                    },
                    {
                        "id": 34322,
                        "name": "account_hourly_stats",
                        "entity_type": "entity/UserTable"
                    },
                    {
                        "id": 34386,
                        "name": "account_stats",
                        "entity_type": "entity/UserTable"
                    }
                ]
            }
        ],
        "table_count": 5,
        "schema_count": 2
    }


@pytest.mark.asyncio
async def test_get_database_metadata_success(mock_context, sample_metadata, expected_simplified_output):
    """Test successful database metadata retrieval with simplified output."""
    # Set up the mock
    client_mock = MagicMock()
    
    # Mock the auth.make_request method to return the sample data
    async def mock_make_request(method, endpoint, **kwargs):
        assert method == "GET"
        assert endpoint == "database/130/metadata"
        assert kwargs.get("params", {}).get("skip_fields") == "true"
        return sample_metadata, 200, None
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_database_metadata(id=130, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that we got the expected simplified structure
        assert result_data["database"] == expected_simplified_output["database"]
        assert result_data["table_count"] == expected_simplified_output["table_count"]
        assert result_data["schema_count"] == expected_simplified_output["schema_count"]
        
        # Check schemas and tables - order might vary due to dict iteration
        schema_names = {schema["name"] for schema in result_data["schemas"]}
        expected_schema_names = {schema["name"] for schema in expected_simplified_output["schemas"]}
        assert schema_names == expected_schema_names
        
        # Verify the mock was called correctly
        client_mock.auth.make_request.assert_called_once()


@pytest.mark.asyncio
async def test_get_database_metadata_api_error(mock_context):
    """Test database metadata retrieval when API returns an error."""
    # Set up the mock to return an error
    client_mock = MagicMock()
    
    async def mock_make_request(method, endpoint, **kwargs):
        return None, 404, "Database not found"
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_database_metadata(id=9999, ctx=mock_context)
        
        # Verify the result is an error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["status_code"] == 404
        assert result_data["error"]["error_type"] == "retrieval_error"
        assert result_data["error"]["message"] == "Database not found"
        assert result_data["error"]["request_info"]["endpoint"] == "/api/database/9999/metadata"


@pytest.mark.asyncio
async def test_get_database_metadata_empty_tables(mock_context):
    """Test database metadata retrieval when no tables are returned."""
    # Sample data with no tables
    sample_data_no_tables = {
        "id": 130,
        "name": "Empty Database",
        "engine": "redshift",
        "timezone": "GMT",
        "tables": []
    }
    
    # Expected output with no tables
    expected_output = {
        "database": {
            "id": 130,
            "name": "Empty Database",
            "engine": "redshift",
            "timezone": "GMT"
        },
        "schemas": [],
        "table_count": 0,
        "schema_count": 0
    }
    
    # Set up the mock
    client_mock = MagicMock()
    
    async def mock_make_request(method, endpoint, **kwargs):
        return sample_data_no_tables, 200, None
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_database_metadata(id=130, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that we got the expected output with empty tables
        assert result_data == expected_output


@pytest.mark.asyncio
async def test_get_database_metadata_missing_fields(mock_context):
    """Test database metadata retrieval when some fields are missing."""
    # Sample data with missing fields
    sample_data_missing_fields = {
        "id": 130,
        "name": "Incomplete DB",
        # missing engine and timezone
        "tables": [
            {
                "id": 34320,
                "name": "account_history",
                # missing schema
                "entity_type": "entity/UserTable"
            },
            {
                # missing id
                "name": "ad_group_history",
                "schema": "googleads_raw",
                # missing entity_type
            }
        ]
    }
    
    # Set up the mock
    client_mock = MagicMock()
    
    async def mock_make_request(method, endpoint, **kwargs):
        return sample_data_missing_fields, 200, None
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_database_metadata(id=130, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check database info with missing fields
        assert result_data["database"]["id"] == 130
        assert result_data["database"]["name"] == "Incomplete DB"
        assert result_data["database"]["engine"] is None
        assert result_data["database"]["timezone"] is None
        
        # Check schemas and tables
        assert result_data["table_count"] == 2
        assert result_data["schema_count"] == 2  # "" schema and "googleads_raw" schema
        
        # Check for tables with missing fields
        empty_schema_tables = next((s["tables"] for s in result_data["schemas"] if s["name"] == ""), None)
        assert empty_schema_tables is not None
        assert len(empty_schema_tables) == 1
        assert empty_schema_tables[0]["id"] == 34320
        assert empty_schema_tables[0]["name"] == "account_history"
        assert empty_schema_tables[0]["entity_type"] == "entity/UserTable"
        
        googleads_schema_tables = next((s["tables"] for s in result_data["schemas"] if s["name"] == "googleads_raw"), None)
        assert googleads_schema_tables is not None
        assert len(googleads_schema_tables) == 1
        assert googleads_schema_tables[0]["id"] is None
        assert googleads_schema_tables[0]["name"] == "ad_group_history"
        assert googleads_schema_tables[0]["entity_type"] is None


@pytest.mark.asyncio
async def test_get_database_metadata_exception(mock_context):
    """Test database metadata retrieval when an exception occurs."""
    # Set up the mock to raise an exception
    client_mock = MagicMock()
    client_mock.auth.make_request = AsyncMock(side_effect=Exception("Connection failed"))
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_database_metadata(id=130, ctx=mock_context)
        
        # Verify the result is an error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["error_type"] == "retrieval_error"
        assert result_data["error"]["message"] == "Connection failed"
