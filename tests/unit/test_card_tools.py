"""
Tests for card tools.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from supermetabase.tools.card import get_card_definition, extract_essential_card_info, get_sql_translation


@pytest.mark.asyncio
async def test_get_card_definition_success(mock_context, sample_card):
    """Test successful card definition retrieval."""
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(return_value=(sample_card, 200, None))
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    with patch("supermetabase.tools.card.get_metabase_client", return_value=client_mock), \
         patch("supermetabase.tools.card.get_sql_translation", return_value=AsyncMock(return_value=None)):
        # Call the tool
        result = await get_card_definition(id=1, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["id"] == 1
        assert result_data["name"] == "Test Card"
        
        # Verify the mock was called correctly
        auth_mock.make_request.assert_called_once_with("GET", "card/1", params={})


@pytest.mark.asyncio
async def test_get_card_definition_with_params(mock_context, sample_card):
    """Test card definition retrieval with query parameters."""
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(return_value=(sample_card, 200, None))
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    with patch("supermetabase.tools.card.get_metabase_client", return_value=client_mock), \
         patch("supermetabase.tools.card.get_sql_translation", return_value=AsyncMock(return_value=None)):
        # Call the tool with parameters
        result = await get_card_definition(
            id=1, 
            ctx=mock_context,
            ignore_view=True
        )
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["id"] == 1
        
        # Verify the mock was called with the correct parameters
        auth_mock.make_request.assert_called_once_with(
            "GET", 
            "card/1", 
            params={"ignore_view": "true"}
        )


@pytest.mark.asyncio
async def test_get_card_definition_error(mock_context):
    """Test card definition retrieval with error."""
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(
        return_value=({"error": "Not found"}, 404, "Card not found")
    )
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    with patch("supermetabase.tools.card.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_card_definition(id=999, ctx=mock_context)
        
        # Verify the result is an error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["message"] == "Card not found"
        assert result_data["error"]["error_type"] == "retrieval_error"


@pytest.mark.asyncio
async def test_get_card_definition_with_mbql_translation(mock_context):
    """Test card definition retrieval with MBQL to SQL translation."""
    # Sample MBQL card data
    sample_mbql_card = {
        "id": 42,
        "name": "MBQL Query Card",
        "query_type": "query",
        "dataset_query": {
            "type": "query",
            "database": 1,
            "query": {
                "source-table": 10,
                "aggregation": [["count"]],
                "breakout": [["field", 20, {"base-type": "type/Text"}]]
            }
        }
    }
    
    # SQL translation result
    sample_sql_translation = "SELECT field_1, COUNT(*) FROM table_10 GROUP BY field_1"
    
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(
        side_effect=[
            (sample_mbql_card, 200, None),  # First call for get_card_definition
            ({"query": sample_sql_translation}, 200, None)  # Second call for SQL translation
        ]
    )
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    with patch("supermetabase.tools.card.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await get_card_definition(id=42, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["id"] == 42
        assert result_data["name"] == "MBQL Query Card"
        assert "sql_translation" in result_data
        assert result_data["sql_translation"] == sample_sql_translation
        
        # Verify the mocks were called correctly
        assert auth_mock.make_request.call_count == 2
        # First call for get_card_definition
        assert auth_mock.make_request.call_args_list[0][0] == ("GET", "card/42")
        # Second call for SQL translation
        assert auth_mock.make_request.call_args_list[1][0] == ("POST", "dataset/native")


def test_extract_essential_card_info():
    """Test extraction of essential card information."""
    # Sample complete card data
    full_card_data = {
        "id": 123,
        "name": "Test Card with Lots of Data",
        "description": "A test card with lots of metadata",
        "type": "question",
        "display": "table",
        "database_id": 1,
        "query_type": "native",
        "last_used_at": "2025-05-22T12:34:56Z",
        "view_count": 42,
        "dataset_query": {
            "type": "native",
            "database": 1,
            "native": {
                "query": "SELECT * FROM test_table",
                "template-tags": {"tag1": {"name": "tag1", "type": "text"}}
            }
        },
        "visualization_settings": {
            "graph.dimensions": ["dim1", "dim2"],
            "graph.metrics": ["metric1"],
            "table.pivot_column": "column1",
            "table.cell_column": "column2",
            "irrelevant_setting": "value",
            "series_settings": {
                "series1": {"color": "#ff0000"}
            }
        },
        "collection": {
            "id": 5,
            "name": "Test Collection",
            "location": "/root/",
            "personal_owner_id": 10,
            "slug": "test_collection"
        },
        "creator": {
            "id": 7,
            "email": "user@example.com",
            "first_name": "Test",
            "last_name": "User",
            "common_name": "Test User"
        },
        "result_metadata": [
            {
                "name": "column1",
                "display_name": "Column 1",
                "base_type": "type/Text",
                "semantic_type": "type/Name",
                "field_ref": ["field", "column1", {"base-type": "type/Text"}],
                "fingerprint": {"global": {"distinct-count": 100}},
                "other_metadata": "value"
            }
        ],
        "parameters": [
            {
                "id": "param1",
                "name": "Parameter 1",
                "type": "string/=",
                "slug": "param_1",
                "target": ["dimension", ["field", 100, null]],
                "values_source_type": "static-list",
                "values_source_config": {"values": ["a", "b", "c"]},
                "default": "a"
            }
        ],
        "dashboard_count": 3,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "embedding_params": null,
        "enable_embedding": false,
        "cache_ttl": null,
        "archived": false,
        "can_write": true
    }
    
    # Extract essential info
    essential_info = extract_essential_card_info(full_card_data)
    
    # Verify the essential fields are present
    assert essential_info["id"] == 123
    assert essential_info["name"] == "Test Card with Lots of Data"
    assert essential_info["description"] == "A test card with lots of metadata"
    assert essential_info["type"] == "question"
    assert essential_info["display"] == "table"
    
    # Verify collection info was simplified
    assert essential_info["collection"]["id"] == 5
    assert essential_info["collection"]["name"] == "Test Collection"
    assert "personal_owner_id" not in essential_info["collection"]
    
    # Verify creator info was simplified
    assert essential_info["creator"]["id"] == 7
    assert essential_info["creator"]["name"] == "Test User"
    assert "email" not in essential_info["creator"]
    
    # Verify dataset query was simplified but kept important parts
    assert essential_info["dataset_query"]["type"] == "native"
    assert essential_info["dataset_query"]["native"]["query"] == "SELECT * FROM test_table"
    assert "template-tags" in essential_info["dataset_query"]["native"]
    
    # Verify visualization settings were simplified
    assert "graph.dimensions" in essential_info["visualization_settings"]
    assert "irrelevant_setting" not in essential_info["visualization_settings"]
    assert "series_settings" in essential_info["visualization_settings"]
    
    # Verify parameters were simplified
    assert len(essential_info["parameters"]) == 1
    assert essential_info["parameters"][0]["id"] == "param1"
    assert essential_info["parameters"][0]["name"] == "Parameter 1"
    assert "values_source_type" in essential_info["parameters"][0]
    assert "default" not in essential_info["parameters"][0]
    
    # Verify result metadata was simplified
    assert len(essential_info["result_metadata"]) == 1
    assert essential_info["result_metadata"][0]["name"] == "column1"
    assert essential_info["result_metadata"][0]["base_type"] == "type/Text"
    assert "fingerprint" not in essential_info["result_metadata"][0]
    
    # Verify other fields were included or excluded as expected
    assert essential_info["dashboard_count"] == 3
    assert "created_at" not in essential_info
    assert "updated_at" not in essential_info
    assert "embedding_params" not in essential_info
    assert "archived" not in essential_info
    
    # Verify that unnecessary runtime data is excluded
    assert "last_used_at" not in essential_info
    assert "view_count" not in essential_info


@pytest.mark.asyncio
async def test_get_sql_translation_success():
    """Test successful MBQL to SQL translation."""
    # Sample MBQL query
    sample_card = {
        "dataset_query": {
            "type": "query",
            "database": 1,
            "query": {
                "source-table": 10,
                "aggregation": [["count"]]
            }
        }
    }
    
    # Expected SQL translation
    expected_sql = "SELECT COUNT(*) FROM table_10"
    
    # Set up the mock
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(
        return_value=({"query": expected_sql}, 200, None)
    )
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    # Call the function
    sql_translation = await get_sql_translation(client_mock, sample_card)
    
    # Verify the result
    assert sql_translation == expected_sql
    
    # Verify the mock was called correctly
    auth_mock.make_request.assert_called_once()
    call_args = auth_mock.make_request.call_args[0]
    assert call_args[0] == "POST"
    assert call_args[1] == "dataset/native"
    

@pytest.mark.asyncio
async def test_get_sql_translation_not_mbql():
    """Test that SQL translation is skipped for non-MBQL queries."""
    # Sample native query
    sample_card = {
        "dataset_query": {
            "type": "native",
            "database": 1,
            "native": {
                "query": "SELECT * FROM table"
            }
        }
    }
    
    # Set up the mock
    client_mock = MagicMock()
    
    # Call the function
    sql_translation = await get_sql_translation(client_mock, sample_card)
    
    # Verify no translation was attempted
    assert sql_translation is None
    assert client_mock.auth.make_request.call_count == 0


@pytest.mark.asyncio
async def test_get_sql_translation_error():
    """Test handling of translation errors."""
    # Sample MBQL query
    sample_card = {
        "dataset_query": {
            "type": "query",
            "database": 1,
            "query": {
                "source-table": 10,
                "aggregation": [["count"]]
            }
        }
    }
    
    # Set up the mock to return an error
    auth_mock = MagicMock()
    auth_mock.make_request = AsyncMock(
        return_value=(None, 500, "Internal server error")
    )
    
    client_mock = MagicMock()
    client_mock.auth = auth_mock
    
    # Call the function
    sql_translation = await get_sql_translation(client_mock, sample_card)
    
    # Verify the result is None on error
    assert sql_translation is None
