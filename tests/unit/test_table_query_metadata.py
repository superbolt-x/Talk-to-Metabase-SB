"""
Tests for get_table_query_metadata tool.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from talk_to_metabase.tools.database import get_table_query_metadata


@pytest.fixture
def sample_table_query_metadata():
    """Sample table query metadata from Metabase API."""
    return {
        "description": None,
        "entity_type": "entity/GenericTable",
        "view_count": 21,
        "schema": "gsheet_raw",
        "database_require_filter": None,
        "db": {
            "uploads_schema_name": None,
            "description": None,
            "features": ["describe-fks", "full-join", "window-functions/cumulative", "test/dynamic-dataset-loading"],
            "uploads_table_prefix": None,
            "cache_field_values_schedule": "0 0 1 * * ? *",
            "timezone": "UTC",
            "is_attached_dwh": False,
            "auto_run_queries": True,
            "metadata_sync_schedule": "0 49 * * * ? *",
            "name": "Bariendo",
            "settings": None,
            "caveats": None,
            "creator_id": 116,
            "is_full_sync": True,
            "updated_at": "2025-05-22T16:49:00.403281Z",
            "cache_ttl": None,
            "details": None,
            "is_sample": False,
            "id": 195,
            "is_on_demand": False,
            "entity_id": "3jR1GYpOMgw9DVClGa2tX",
            "engine": "redshift",
            "initial_sync_status": "complete",
            "is_audit": False,
            "dbms_version": {"flavor": "Redshift", "version": "8.0.2", "semantic-version": [8, 0]},
            "uploads_enabled": False,
            "refingerprint": None,
            "created_at": "2024-05-02T19:27:34.258413Z",
            "points_of_interest": None
        },
        "show_in_getting_started": False,
        "name": "meta_ads_frequency_l_30_d",
        "fields": [
            {
                "description": None,
                "database_type": "bigint",
                "semantic_type": "type/PK",
                "table_id": 50112,
                "coercion_strategy": None,
                "database_indexed": None,
                "name": "_row",
                "fingerprint_version": 0,
                "has_field_values": "none",
                "settings": None,
                "caveats": None,
                "fk_target_field_id": None,
                "dimensions": [],
                "dimension_options": [],
                "updated_at": "2025-04-24T19:36:29.883991Z",
                "custom_position": 0,
                "effective_type": "type/BigInteger",
                "active": True,
                "nfc_path": None,
                "parent_id": None,
                "id": 50711061,
                "last_analyzed": None,
                "database_partitioned": None,
                "database_is_auto_increment": False,
                "json_unfolding": False,
                "position": 0,
                "entity_id": None,
                "visibility_type": "normal",
                "default_dimension_option": None,
                "target": None,
                "preview_display": True,
                "display_name": "Row",
                "database_position": 0,
                "database_required": False,
                "name_field": None,
                "fingerprint": None,
                "created_at": "2025-04-24T19:36:29.883991Z",
                "base_type": "type/BigInteger",
                "points_of_interest": None
            },
            {
                "description": None,
                "database_type": "timestamp with time zone",
                "semantic_type": None,
                "table_id": 50112,
                "coercion_strategy": None,
                "database_indexed": None,
                "name": "_fivetran_synced",
                "fingerprint_version": 5,
                "has_field_values": "none",
                "settings": None,
                "caveats": None,
                "fk_target_field_id": None,
                "dimensions": [],
                "dimension_options": ["11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25"],
                "updated_at": "2025-04-24T19:36:48.036037Z",
                "custom_position": 0,
                "effective_type": "type/DateTimeWithLocalTZ",
                "active": True,
                "nfc_path": None,
                "parent_id": None,
                "id": 50711055,
                "last_analyzed": "2025-04-24T19:36:48.036037Z",
                "database_partitioned": None,
                "database_is_auto_increment": False,
                "json_unfolding": False,
                "position": 1,
                "entity_id": None,
                "visibility_type": "normal",
                "default_dimension_option": "13",
                "target": None,
                "preview_display": True,
                "display_name": "Fivetran Synced",
                "database_position": 1,
                "database_required": False,
                "name_field": None,
                "fingerprint": {
                    "global": {"distinct-count": 3, "nil%": 0.0},
                    "type": {"type/DateTime": {"earliest": "2025-04-24T19:23:09.689Z", "latest": "2025-04-24T19:23:09.691Z"}}
                },
                "created_at": "2025-04-24T19:36:29.883991Z",
                "base_type": "type/DateTimeWithLocalTZ",
                "points_of_interest": None
            },
            {
                "description": None,
                "database_type": "character varying",
                "semantic_type": "type/Category",
                "table_id": 50112,
                "coercion_strategy": None,
                "database_indexed": None,
                "name": "campaign_name",
                "fingerprint_version": 5,
                "has_field_values": "list",
                "settings": None,
                "caveats": None,
                "fk_target_field_id": None,
                "dimensions": [],
                "dimension_options": [],
                "updated_at": "2025-04-24T19:36:48.036037Z",
                "custom_position": 0,
                "effective_type": "type/Text",
                "active": True,
                "nfc_path": None,
                "parent_id": None,
                "id": 50711060,
                "last_analyzed": "2025-04-24T19:36:48.036037Z",
                "database_partitioned": None,
                "database_is_auto_increment": False,
                "json_unfolding": False,
                "position": 2,
                "entity_id": None,
                "visibility_type": "normal",
                "default_dimension_option": None,
                "target": None,
                "preview_display": True,
                "display_name": "Campaign Name",
                "database_position": 2,
                "database_required": False,
                "name_field": None,
                "fingerprint": {
                    "global": {"distinct-count": 6, "nil%": 0.0},
                    "type": {"type/Text": {"percent-json": 0.0, "percent-url": 0.0, "percent-email": 0.0, "percent-state": 0.0, "average-length": 75.4375}}
                },
                "created_at": "2025-04-24T19:36:29.883991Z",
                "base_type": "type/Text",
                "points_of_interest": None
            }
        ],
        "caveats": None,
        "segments": [],
        "dimension_options": {},
        "updated_at": "2025-05-22T18:49:02.608548Z",
        "active": True,
        "id": 50112,
        "db_id": 195,
        "entity_id": "kOACRhwrFrDfjTsuRH8K2",
        "visibility_type": None,
        "field_order": "database",
        "is_upload": False,
        "initial_sync_status": "complete",
        "display_name": "Meta Ads Frequency L 30 D",
        "metrics": [],
        "created_at": "2025-04-24T19:36:28.285984Z",
        "estimated_row_count": None,
        "points_of_interest": None
    }


@pytest.fixture
def expected_simplified_table_metadata():
    """Expected simplified output from the get_table_query_metadata tool."""
    return {
        "table": {
            "id": 50112,
            "name": "meta_ads_frequency_l_30_d",
            "schema": "gsheet_raw",
            "entity_type": "entity/GenericTable",
            "description": None,
            "view_count": 21
        },
        "database": {
            "id": 195,
            "name": "Bariendo",
            "engine": "redshift",
            "timezone": "UTC"
        },
        "fields": [
            {
                "id": 50711061,
                "name": "_row",
                "display_name": "Row",
                "base_type": "type/BigInteger",
                "effective_type": "type/BigInteger",
                "semantic_type": "type/PK",
                "database_type": "bigint",
                "active": True,
                "visibility_type": "normal",
                "has_field_values": "none",
                "position": 0
            },
            {
                "id": 50711055,
                "name": "_fivetran_synced",
                "display_name": "Fivetran Synced",
                "base_type": "type/DateTimeWithLocalTZ",
                "effective_type": "type/DateTimeWithLocalTZ",
                "semantic_type": None,
                "database_type": "timestamp with time zone",
                "active": True,
                "visibility_type": "normal",
                "has_field_values": "none",
                "position": 1
            },
            {
                "id": 50711060,
                "name": "campaign_name",
                "display_name": "Campaign Name",
                "base_type": "type/Text",
                "effective_type": "type/Text",
                "semantic_type": "type/Category",
                "database_type": "character varying",
                "active": True,
                "visibility_type": "normal",
                "has_field_values": "list",
                "position": 2
            }
        ],
        "field_count": 3,
        "primary_key_fields": ["_row"],
        "date_fields": ["_fivetran_synced"]
    }


@pytest.mark.asyncio
async def test_get_table_query_metadata_success(mock_context, sample_table_query_metadata, expected_simplified_table_metadata):
    """Test successful table query metadata retrieval with simplified output."""
    # Set up the mock
    client_mock = MagicMock()
    
    # Mock the auth.make_request method to return the sample data
    async def mock_make_request(method, endpoint, params=None, **kwargs):
        return sample_table_query_metadata, 200, None
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_table_query_metadata(id=50112, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that we got the expected simplified structure
        assert result_data == expected_simplified_table_metadata
        
        # Verify the mock was called correctly
        client_mock.auth.make_request.assert_called_once_with("GET", "table/50112/query_metadata", params={})


@pytest.mark.asyncio
async def test_get_table_query_metadata_with_parameters(mock_context, sample_table_query_metadata):
    """Test table query metadata with optional parameters."""
    # Set up the mock
    client_mock = MagicMock()
    
    async def mock_make_request(method, endpoint, params=None, **kwargs):
        return sample_table_query_metadata, 200, None
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool with optional parameters
        result = await get_table_query_metadata(
            id=50112, 
            ctx=mock_context,
            include_sensitive_fields=True,
            include_hidden_fields=True,
            include_editable_data_model=True
        )
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that we got valid structure
        assert "table" in result_data
        assert "database" in result_data
        assert "fields" in result_data
        
        # Verify fields contain only essential information (no fingerprint or dimension_options_count)
        for field in result_data["fields"]:
            assert "fingerprint" not in field
            assert "dimension_options_count" not in field
            # Verify essential fields are present
            assert "id" in field
            assert "name" in field
            assert "base_type" in field
        
        # Verify the mock was called with correct parameters
        expected_params = {
            "include_sensitive_fields": "true",
            "include_hidden_fields": "true",
            "include_editable_data_model": "true"
        }
        client_mock.auth.make_request.assert_called_once_with("GET", "table/50112/query_metadata", params=expected_params)


@pytest.mark.asyncio
async def test_get_table_query_metadata_api_error(mock_context):
    """Test table query metadata when API returns an error."""
    # Set up the mock to return an error
    client_mock = MagicMock()
    
    async def mock_make_request(method, endpoint, params=None, **kwargs):
        return None, 404, "Table not found"
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_table_query_metadata(id=99999, ctx=mock_context)
        
        # Verify the result is an error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["status_code"] == 404
        assert result_data["error"]["error_type"] == "retrieval_error"
        assert result_data["error"]["message"] == "Table not found"


@pytest.mark.asyncio
async def test_get_table_query_metadata_exception(mock_context):
    """Test table query metadata when an exception occurs."""
    # Set up the mock to raise an exception
    client_mock = MagicMock()
    client_mock.auth.make_request = AsyncMock(side_effect=Exception("Connection failed"))
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_table_query_metadata(id=50112, ctx=mock_context)
        
        # Verify the result is an error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["error_type"] == "retrieval_error"
        assert result_data["error"]["message"] == "Connection failed"


@pytest.mark.asyncio
async def test_get_table_query_metadata_missing_fields(mock_context):
    """Test table query metadata when some data is missing."""
    # Create table data with missing fields
    incomplete_table_data = {
        "id": 50112,
        "name": "test_table",
        # schema missing
        "entity_type": "entity/GenericTable",
        # description missing  
        # view_count missing
        "db": {
            "id": 195,
            "name": "Test DB",
            "engine": "postgres",
            # timezone missing
        },
        "fields": [
            {
                "id": 1,
                "name": "test_field",
                "display_name": "Test Field",
                "base_type": "type/Text",
                "effective_type": "type/Text",
                # semantic_type missing
                "database_type": "varchar",
                "active": True,
                "visibility_type": "normal",
                "has_field_values": "none",
                "position": 0
            }
        ]
    }
    
    expected_output = {
        "table": {
            "id": 50112,
            "name": "test_table",
            "schema": None,  # Missing schema becomes None
            "entity_type": "entity/GenericTable",
            "description": None,
            "view_count": None  # Missing view_count becomes None
        },
        "database": {
            "id": 195,
            "name": "Test DB",
            "engine": "postgres",
            "timezone": None  # Missing timezone becomes None
        },
        "fields": [
            {
                "id": 1,
                "name": "test_field",
                "display_name": "Test Field",
                "base_type": "type/Text",
                "effective_type": "type/Text",
                "semantic_type": None,  # Missing semantic_type becomes None
                "database_type": "varchar",
                "active": True,
                "visibility_type": "normal",
                "has_field_values": "none",
                "position": 0
            }
        ],
        "field_count": 1,
        "primary_key_fields": [],  # No PK fields
        "date_fields": []  # No date fields
    }
    
    # Set up the mock
    client_mock = MagicMock()
    
    async def mock_make_request(method, endpoint, params=None, **kwargs):
        return incomplete_table_data, 200, None
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_table_query_metadata(id=50112, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that we got the expected output with None values for missing fields
        assert result_data == expected_output


@pytest.mark.asyncio
async def test_get_table_query_metadata_field_categorization(mock_context):
    """Test that fields are correctly categorized as primary keys and date fields."""
    # Create table data with various field types
    table_data_with_various_fields = {
        "id": 50112,
        "name": "test_table",
        "schema": "test_schema",
        "entity_type": "entity/GenericTable",
        "description": None,
        "view_count": 5,
        "db": {
            "id": 195,
            "name": "Test DB",
            "engine": "postgres",
            "timezone": "UTC"
        },
        "fields": [
            {
                "id": 1,
                "name": "id",
                "display_name": "ID",
                "base_type": "type/BigInteger",
                "effective_type": "type/BigInteger",
                "semantic_type": "type/PK",  # Primary key
                "database_type": "bigint",
                "active": True,
                "visibility_type": "normal",
                "has_field_values": "none",
                "position": 0
            },
            {
                "id": 2,
                "name": "created_at",
                "display_name": "Created At",
                "base_type": "type/DateTime",  # Date field
                "effective_type": "type/DateTime",
                "semantic_type": "type/CreationTimestamp",
                "database_type": "timestamp",
                "active": True,
                "visibility_type": "normal",
                "has_field_values": "none",
                "position": 1
            },
            {
                "id": 3,
                "name": "updated_date",
                "display_name": "Updated Date",
                "base_type": "type/Date",  # Another date field
                "effective_type": "type/Date",
                "semantic_type": None,
                "database_type": "date",
                "active": True,
                "visibility_type": "normal",
                "has_field_values": "none",
                "position": 2
            },
            {
                "id": 4,
                "name": "name",
                "display_name": "Name",
                "base_type": "type/Text",  # Regular text field
                "effective_type": "type/Text",
                "semantic_type": "type/Name",
                "database_type": "varchar",
                "active": True,
                "visibility_type": "normal",
                "has_field_values": "list",
                "position": 3
            }
        ]
    }
    
    # Set up the mock
    client_mock = MagicMock()
    
    async def mock_make_request(method, endpoint, params=None, **kwargs):
        return table_data_with_various_fields, 200, None
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_table_query_metadata(id=50112, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check field categorization
        assert result_data["field_count"] == 4
        assert result_data["primary_key_fields"] == ["id"]
        assert set(result_data["date_fields"]) == {"created_at", "updated_date"}
        
        # Verify fields are sorted by position
        field_positions = [field["position"] for field in result_data["fields"]]
        assert field_positions == sorted(field_positions)
        
        # Verify no optional fields are included
        for field in result_data["fields"]:
            assert "fingerprint" not in field
            assert "dimension_options_count" not in field
            assert "dimension_options" not in field


@pytest.mark.asyncio
async def test_get_table_query_metadata_empty_fields(mock_context):
    """Test table query metadata when table has no fields."""
    # Create table data with empty fields array
    table_data_no_fields = {
        "id": 50112,
        "name": "empty_table",
        "schema": "test_schema",
        "entity_type": "entity/GenericTable",
        "description": "A table with no fields",
        "view_count": 0,
        "db": {
            "id": 195,
            "name": "Test DB",
            "engine": "postgres",
            "timezone": "UTC"
        },
        "fields": []  # Empty fields
    }
    
    expected_output = {
        "table": {
            "id": 50112,
            "name": "empty_table",
            "schema": "test_schema",
            "entity_type": "entity/GenericTable",
            "description": "A table with no fields",
            "view_count": 0
        },
        "database": {
            "id": 195,
            "name": "Test DB",
            "engine": "postgres",
            "timezone": "UTC"
        },
        "fields": [],
        "field_count": 0,
        "primary_key_fields": [],
        "date_fields": []
    }
    
    # Set up the mock
    client_mock = MagicMock()
    
    async def mock_make_request(method, endpoint, params=None, **kwargs):
        return table_data_no_fields, 200, None
    
    client_mock.auth.make_request = AsyncMock(side_effect=mock_make_request)
    
    with patch("talk_to_metabase.tools.database.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_table_query_metadata(id=50112, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check that we got the expected output for empty fields
        assert result_data == expected_output
