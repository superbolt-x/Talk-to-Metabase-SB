"""
Unit tests for collection tools.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from supermetabase.tools.collection import explore_collection_tree, view_collection_contents


@pytest.mark.asyncio
async def test_explore_collection_tree_root_success(mock_context):
    """Test successful exploration of root collection tree."""
    # Sample mixed data with various item types
    sample_data = {
        "total": 7,
        "data": [
            {
                "id": 1,
                "name": "Marketing Collection",
                "model": "collection",
                "location": "/"
            },
            {
                "id": 2,
                "name": "Sales Collection", 
                "model": "collection",
                "location": "/"
            },
            {
                "id": 10,
                "name": "Dashboard 1",
                "model": "dashboard"
            },
            {
                "id": 11,
                "name": "Dashboard 2", 
                "model": "dashboard"
            },
            {
                "id": 20,
                "name": "Card 1",
                "model": "card"
            },
            {
                "id": 30,
                "name": "Dataset 1",
                "model": "dataset"
            },
            {
                "id": 40,
                "name": "Snippet 1",
                "model": "snippet"
            }
        ]
    }
    
    client_mock = MagicMock()
    client_mock.auth.make_request = AsyncMock(return_value=(sample_data, 200, None))
    
    with patch("supermetabase.tools.collection.get_metabase_client", return_value=client_mock):
        result = await explore_collection_tree(ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Should show only collections in child_collections
        assert result_data["collection_id"] is None
        assert len(result_data["child_collections"]) == 2
        
        # Check collection details
        collections = result_data["child_collections"]
        assert collections[0]["id"] == 1
        assert collections[0]["name"] == "Marketing Collection"
        assert collections[0]["model"] == "collection"
        assert collections[0]["location"] == "/"
        
        # Check comprehensive content summary includes all types
        summary = result_data["content_summary"]
        assert summary["collection"] == 2
        assert summary["dashboard"] == 2
        assert summary["card"] == 1
        assert summary["dataset"] == 1
        assert summary["timeline"] == 0
        assert summary["snippet"] == 1
        assert summary["pulse"] == 0
        assert summary["metric"] == 0
        
        # Verify API call was made without model filter (to get all items)
        client_mock.auth.make_request.assert_called_once_with(
            "GET", "collection/root/items", params={"archived": "false"}
        )


@pytest.mark.asyncio
async def test_explore_collection_tree_specific_collection(mock_context):
    """Test exploration of a specific collection's tree."""
    sample_data = {
        "total": 3,
        "data": [
            {
                "id": 5,
                "name": "Subcollection A",
                "model": "collection"
            },
            {
                "id": 6,
                "name": "Subcollection B",
                "model": "collection" 
            },
            {
                "id": 15,
                "name": "Dashboard in Collection",
                "model": "dashboard"
            }
        ]
    }
    
    client_mock = MagicMock()
    client_mock.auth.make_request = AsyncMock(return_value=(sample_data, 200, None))
    
    with patch("supermetabase.tools.collection.get_metabase_client", return_value=client_mock):
        result = await explore_collection_tree(collection_id=123, ctx=mock_context)
        
        result_data = json.loads(result)
        
        # Should show specific collection ID
        assert result_data["collection_id"] == 123
        assert len(result_data["child_collections"]) == 2
        
        # Check content summary
        summary = result_data["content_summary"]
        assert summary["collection"] == 2
        assert summary["dashboard"] == 1
        assert summary["card"] == 0
        
        # Verify correct endpoint was called
        client_mock.auth.make_request.assert_called_once_with(
            "GET", "collection/123/items", params={"archived": "false"}
        )


@pytest.mark.asyncio
async def test_view_collection_contents_all_items(mock_context):
    """Test viewing all contents of a collection."""
    sample_data = {
        "total": 5,
        "data": [
            {
                "id": 1,
                "name": "Collection 1",
                "model": "collection",
                "description": "Should be stripped",
                "can_write": True
            },
            {
                "id": 10,
                "name": "Dashboard 1",
                "model": "dashboard",
                "description": "Should be stripped"
            },
            {
                "id": 20,
                "name": "Card 1", 
                "model": "card",
                "display": "table"
            },
            {
                "id": 30,
                "name": "Dataset 1",
                "model": "dataset"
            },
            {
                "id": 100,
                "name": "Database 1",
                "model": "database"  # Should be filtered out
            }
        ]
    }
    
    client_mock = MagicMock()
    client_mock.auth.make_request = AsyncMock(return_value=(sample_data, 200, None))
    
    with patch("supermetabase.tools.collection.get_metabase_client", return_value=client_mock):
        result = await view_collection_contents(ctx=mock_context)
        
        result_data = json.loads(result)
        
        # Should show all items except database
        assert result_data["collection_id"] is None
        assert len(result_data["items"]) == 4
        
        # Check items are simplified
        for item in result_data["items"]:
            expected_keys = {"id", "name", "model"}
            assert set(item.keys()) <= expected_keys  # May have location too
            assert "description" not in item
            assert "can_write" not in item
            assert "display" not in item
        
        # Check content summary
        summary = result_data["content_summary"]
        assert summary["collection"] == 1
        assert summary["dashboard"] == 1
        assert summary["card"] == 1
        assert summary["dataset"] == 1
        assert "database" not in summary  # Shouldn't appear
        
        # Verify API call made without model filter
        client_mock.auth.make_request.assert_called_once_with(
            "GET", "collection/root/items", params={"archived": "false"}
        )


@pytest.mark.asyncio
async def test_view_collection_contents_filtered_models(mock_context):
    """Test viewing collection contents with model filter."""
    sample_data = {
        "total": 3,
        "data": [
            {
                "id": 10,
                "name": "Dashboard 1",
                "model": "dashboard"
            },
            {
                "id": 11,
                "name": "Dashboard 2",
                "model": "dashboard"
            },
            {
                "id": 20,
                "name": "Card 1",
                "model": "card"
            }
        ]
    }
    
    client_mock = MagicMock()
    client_mock.auth.make_request = AsyncMock(return_value=(sample_data, 200, None))
    
    with patch("supermetabase.tools.collection.get_metabase_client", return_value=client_mock):
        # Filter for only dashboards
        result = await view_collection_contents(
            ctx=mock_context, 
            models=["dashboard"]
        )
        
        result_data = json.loads(result)
        
        # Should show filtered items
        assert len(result_data["items"]) == 2  # Filtered
        
        # All items should be dashboards (filtered)
        models_in_items = [item["model"] for item in result_data["items"]]
        assert all(model == "dashboard" for model in models_in_items)
        
        # Content summary should reflect all items returned
        summary = result_data["content_summary"]
        assert summary["dashboard"] == 2
        assert summary["card"] == 1
        
        # Verify API call made with model filter
        client_mock.auth.make_request.assert_called_once_with(
            "GET", "collection/root/items", params={"archived": "false", "models": ["dashboard"]}
        )


@pytest.mark.asyncio
async def test_explore_collection_tree_empty_collection(mock_context):
    """Test exploring tree of empty collection."""
    sample_data = {
        "total": 0,
        "data": []
    }
    
    client_mock = MagicMock()
    client_mock.auth.make_request = AsyncMock(return_value=(sample_data, 200, None))
    
    with patch("supermetabase.tools.collection.get_metabase_client", return_value=client_mock):
        result = await explore_collection_tree(ctx=mock_context)
        
        result_data = json.loads(result)
        
        # Should handle empty collection
        assert result_data["collection_id"] is None
        assert len(result_data["child_collections"]) == 0
        
        # All counts should be 0
        summary = result_data["content_summary"]
        for model_type in ["dashboard", "card", "collection", "dataset", "timeline", "snippet", "pulse", "metric"]:
            assert summary[model_type] == 0


@pytest.mark.asyncio
async def test_view_collection_contents_empty_collection(mock_context):
    """Test viewing contents of empty collection."""
    sample_data = {
        "total": 0,
        "data": []
    }
    
    client_mock = MagicMock()
    client_mock.auth.make_request = AsyncMock(return_value=(sample_data, 200, None))
    
    with patch("supermetabase.tools.collection.get_metabase_client", return_value=client_mock):
        result = await view_collection_contents(ctx=mock_context)
        
        result_data = json.loads(result)
        
        # Should handle empty collection
        assert result_data["collection_id"] is None
        assert len(result_data["items"]) == 0
        
        # All counts should be 0
        summary = result_data["content_summary"]
        for model_type in ["dashboard", "card", "collection", "dataset", "timeline", "snippet", "pulse", "metric"]:
            assert summary[model_type] == 0


@pytest.mark.asyncio
async def test_collection_tools_error_handling(mock_context):
    """Test error handling for both collection tools."""
    client_mock = MagicMock()
    client_mock.auth.make_request = AsyncMock(return_value=(None, 404, "Collection not found"))
    
    with patch("supermetabase.tools.collection.get_metabase_client", return_value=client_mock):
        # Test explore_collection_tree error handling
        result1 = await explore_collection_tree(collection_id=9999, ctx=mock_context)
        result1_data = json.loads(result1)
        assert result1_data["success"] == False
        assert result1_data["error"]["status_code"] == 404
        
        # Test view_collection_contents error handling  
        result2 = await view_collection_contents(collection_id=9999, ctx=mock_context)
        result2_data = json.loads(result2)
        assert result2_data["success"] == False
        assert result2_data["error"]["status_code"] == 404
