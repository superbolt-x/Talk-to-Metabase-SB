"""
Tests for database tools.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from talk_to_metabase.tools.database import list_databases


@pytest.fixture
def sample_database_data():
    """Sample database data from Metabase API."""
    return [
        {
            "uploads_schema_name": None,
            "description": None,
            "features": ["describe-fks", "full-join", "window-functions/cumulative"],
            "uploads_table_prefix": None,
            "cache_field_values_schedule": "0 0 8 * * ? *",
            "timezone": "UTC",
            "is_attached_dwh": False,
            "auto_run_queries": True,
            "metadata_sync_schedule": "0 48 * * * ? *",
            "name": "Ask Tia",
            "settings": None,
            "caveats": None,
            "creator_id": 7,
            "is_full_sync": True,
            "updated_at": "2025-05-22T08:48:00.350795Z",
            "native_permissions": "write",
            "cache_ttl": None,
            "details": {
                "host": "redshift-cluster-3.ceq0oiwytao0.us-east-1.redshift.amazonaws.com",
                "port": 5439,
                "db": "asktia",
                "schema-filters-type": "all",
                "user": "sgsuser",
                "password": "**MetabasePass**",
                "tunnel-enabled": False,
                "advanced-options": False
            },
            "is_sample": False,
            "id": 130,
            "is_on_demand": False,
            "entity_id": "eVOlrnztsQF8R8Igl-F8p",
            "engine": "redshift",
            "initial_sync_status": "complete",
            "is_audit": False,
            "dbms_version": {
                "flavor": "Redshift",
                "version": "8.0.2",
                "semantic-version": [8, 0]
            },
            "uploads_enabled": False,
            "refingerprint": None,
            "created_at": "2022-10-27T14:05:02.860642Z",
            "points_of_interest": None,
            "can_upload": False
        },
        {
            "uploads_schema_name": None,
            "description": None,
            "features": ["describe-fks", "full-join", "window-functions/cumulative"],
            "uploads_table_prefix": None,
            "cache_field_values_schedule": "0 0 16 * * ? *",
            "timezone": "UTC",
            "is_attached_dwh": False,
            "auto_run_queries": True,
            "metadata_sync_schedule": "0 19 * * * ? *",
            "name": "AUrate",
            "settings": {
                "persist-models-enabled": True
            },
            "caveats": None,
            "creator_id": 1,
            "is_full_sync": True,
            "updated_at": "2025-05-22T14:19:00.706459Z",
            "native_permissions": "write",
            "cache_ttl": None,
            "details": {
                "host": "redshift-cluster-3.ceq0oiwytao0.us-east-1.redshift.amazonaws.com",
                "port": 5439,
                "db": "aurate",
                "user": "sgsuser",
                "password": "**MetabasePass**",
                "tunnel-enabled": False,
                "schema-filters-type": "all",
                "advanced-options": False
            },
            "is_sample": False,
            "id": 144,
            "is_on_demand": False,
            "entity_id": "x5E_zENO7DanE4i6F4RcL",
            "engine": "redshift",
            "initial_sync_status": "complete",
            "is_audit": False,
            "dbms_version": {
                "flavor": "Redshift",
                "version": "8.0.2",
                "semantic-version": [8, 0]
            },
            "uploads_enabled": False,
            "refingerprint": None,
            "created_at": "2022-11-08T10:27:22.815706Z",
            "points_of_interest": None,
            "can_upload": False
        },
        {
            "uploads_schema_name": None,
            "description": None,
            "features": ["describe-fks", "full-join", "window-functions/cumulative"],
            "uploads_table_prefix": None,
            "cache_field_values_schedule": "0 0 12 * * ? *",
            "timezone": "GMT",
            "is_attached_dwh": False,
            "auto_run_queries": True,
            "metadata_sync_schedule": "0 17 * * * ? *",
            "name": "Baret Scholars",
            "settings": None,
            "caveats": None,
            "creator_id": 116,
            "is_full_sync": True,
            "updated_at": "2025-05-22T14:17:00.278699Z",
            "native_permissions": "write",
            "cache_ttl": None,
            "details": {
                "host": "redshift-cluster-3.ceq0oiwytao0.us-east-1.redshift.amazonaws.com",
                "port": 5439,
                "db": "baretscholars",
                "schema-filters-type": "all",
                "user": "sgsuser",
                "password": "**MetabasePass**",
                "tunnel-enabled": False,
                "advanced-options": False
            },
            "is_sample": False,
            "id": 189,
            "is_on_demand": False,
            "entity_id": "tXdnqscFNT2fr3kI-jGsy",
            "engine": "redshift",
            "initial_sync_status": "complete",
            "is_audit": False,
            "dbms_version": {
                "flavor": "Redshift",
                "version": "8.0.2",
                "semantic-version": [8, 0]
            },
            "uploads_enabled": False,
            "refingerprint": None,
            "created_at": "2024-02-21T19:06:31.575771Z",
            "points_of_interest": None,
            "can_upload": False
        }
    ]


@pytest.fixture
def expected_simplified_output():
    """Expected simplified output from the list_databases tool."""
    return {
        "databases": [
            {
                "id": 130,
                "name": "Ask Tia",
                "engine": "redshift"
            },
            {
                "id": 144,
                "name": "AUrate",
                "engine": "redshift"
            },
            {
                "id": 189,
                "name": "Baret Scholars",
                "engine": "redshift"
            }
        ]
    }


@pytest.mark.asyncio
async def test_list_databases_success(mock_context, sample_database_data, expected_simplified_output):
    """Test successful database listing with simplified output."""
    # Set up the mock
    client_mock = MagicMock()
    
    # Mock the auth.make_request method to return the sample data
    async def mock_make_request(method, endpoint, **kwargs):
        return sample_database_data, 200, None
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await list_databases(ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that we got the expected simplified structure
        assert result_data == expected_simplified_output
        
        # Verify the mock was called correctly
        client_mock.auth.make_request.assert_called_once_with("GET", "database")


@pytest.mark.asyncio
async def test_list_databases_with_dict_response(mock_context, sample_database_data, expected_simplified_output):
    """Test database listing when API returns data wrapped in a dict with 'data' key."""
    # Set up the mock with data wrapped in a dict
    client_mock = MagicMock()
    
    async def mock_make_request(method, endpoint, **kwargs):
        return {"data": sample_database_data}, 200, None
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await list_databases(ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that we got the expected simplified structure
        assert result_data == expected_simplified_output
        
        # Verify the mock was called correctly
        client_mock.auth.make_request.assert_called_once_with("GET", "database")


@pytest.mark.asyncio
async def test_list_databases_api_error(mock_context):
    """Test database listing when API returns an error."""
    # Set up the mock to return an error
    client_mock = MagicMock()
    
    async def mock_make_request(method, endpoint, **kwargs):
        return None, 500, "Internal server error"
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await list_databases(ctx=mock_context)
        
        # Verify the result is an error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["status_code"] == 500
        assert result_data["error"]["error_type"] == "retrieval_error"
        assert result_data["error"]["message"] == "Internal server error"


@pytest.mark.asyncio
async def test_list_databases_unexpected_format(mock_context):
    """Test database listing when API returns unexpected data format."""
    # Set up the mock to return unexpected format
    client_mock = MagicMock()
    
    async def mock_make_request(method, endpoint, **kwargs):
        return "unexpected string response", 200, None
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await list_databases(ctx=mock_context)
        
        # Verify the result is an error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["error_type"] == "unexpected_format"
        assert "Unexpected response format" in result_data["error"]["message"]


@pytest.mark.asyncio
async def test_list_databases_exception(mock_context):
    """Test database listing when an exception occurs."""
    # Set up the mock to raise an exception
    client_mock = MagicMock()
    client_mock.auth.make_request = AsyncMock(side_effect=Exception("Connection failed"))
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await list_databases(ctx=mock_context)
        
        # Verify the result is an error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["error_type"] == "retrieval_error"
        assert result_data["error"]["message"] == "Connection failed"


@pytest.mark.asyncio
async def test_list_databases_missing_fields(mock_context):
    """Test database listing when some database entries have missing fields."""
    # Create database data with missing fields
    incomplete_database_data = [
        {
            "id": 130,
            "name": "Ask Tia",
            "engine": "redshift"
            # All other fields missing
        },
        {
            "id": 144,
            # name missing
            "engine": "redshift"
        },
        {
            # id missing
            "name": "Incomplete DB",
            "engine": "postgres"
        }
    ]
    
    expected_output = {
        "databases": [
            {
                "id": 130,
                "name": "Ask Tia",
                "engine": "redshift"
            },
            {
                "id": 144,
                "name": None,  # Missing name becomes None
                "engine": "redshift"
            },
            {
                "id": None,  # Missing id becomes None
                "name": "Incomplete DB",
                "engine": "postgres"
            }
        ]
    }
    
    # Set up the mock
    client_mock = MagicMock()
    
    async def mock_make_request(method, endpoint, **kwargs):
        return incomplete_database_data, 200, None
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await list_databases(ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that we got the expected output with None values for missing fields
        assert result_data == expected_output


@pytest.mark.asyncio
async def test_list_databases_empty_response(mock_context):
    """Test database listing when API returns empty list."""
    # Set up the mock to return empty list
    client_mock = MagicMock()
    
    async def mock_make_request(method, endpoint, **kwargs):
        return [], 200, None
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await list_databases(ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that we got empty databases list
        expected_output = {"databases": []}
        assert result_data == expected_output
