"""
Tests for search tools.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from supermetabase.tools.search import search_resources


@pytest.fixture
def sample_search_results():
    """Sample search results data."""
    return [
        {
            "id": 1,
            "name": "Test Dashboard",
            "description": "A test dashboard",
            "model": "dashboard",
            "archived": False,
            "collection_id": 1,
            "collection_name": "Test Collection"
        },
        {
            "id": 2,
            "name": "Test Card",
            "description": "A test card",
            "model": "card",
            "archived": False,
            "collection_id": 1,
            "collection_name": "Test Collection"
        }
    ]


@pytest.fixture
def sample_search_results_paginated():
    """Sample paginated search results data."""
    # Generate 100 sample results for pagination testing
    results = []
    for i in range(1, 101):
        result_type = "dashboard" if i % 2 == 0 else "card"
        results.append({
            "id": i,
            "name": f"Test {result_type.capitalize()} {i}",
            "description": f"A test {result_type} {i}",
            "model": result_type,
            "archived": False,
            "collection_id": 1,
            "collection_name": "Test Collection"
        })
    return results


@pytest.mark.asyncio
async def test_search_resources_basic_success(mock_context, sample_search_results):
    """Test successful basic search with query only."""
    # Set up the mock
    client_mock = MagicMock()
    client_mock.search = AsyncMock(return_value={"results": sample_search_results, "pagination": {"page": 1, "page_size": 20, "total_count": 2, "total_pages": 1, "has_more": False}})
    
    with patch("supermetabase.tools.search.get_metabase_client", return_value=client_mock):
        # Call the tool with a simple query
        result = await search_resources(ctx=mock_context, q="test")
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert "results" in result_data
        assert len(result_data["results"]) == 2
        assert result_data["results"][0]["name"] == "Test Dashboard"
        assert result_data["results"][1]["name"] == "Test Card"
        
        # Verify the mock was called correctly
        client_mock.search.assert_called_once()
        assert client_mock.search.call_args[1]["query"] == "test"


@pytest.mark.asyncio
async def test_search_resources_advanced_filters(mock_context, sample_search_results):
    """Test search with advanced filters."""
    # Set up the mock
    client_mock = MagicMock()
    client_mock.search = AsyncMock(return_value={"results": sample_search_results, "pagination": {"page": 1, "page_size": 20, "total_count": 2, "total_pages": 1, "has_more": False}})
    
    with patch("supermetabase.tools.search.get_metabase_client", return_value=client_mock):
        # Call the tool with multiple filters
        result = await search_resources(
            ctx=mock_context,
            q="test",
            models=["dashboard", "card"],
            archived=False,
            table_db_id=1,
            filter_items_in_personal_collection="exclude",
            verified=True
        )
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert "results" in result_data
        assert len(result_data["results"]) == 2
        
        # Verify the mock was called with the correct parameters
        client_mock.search.assert_called_once()
        call_kwargs = client_mock.search.call_args[1]
        assert call_kwargs["query"] == "test"
        assert call_kwargs["models"] == ["dashboard", "card"]
        assert call_kwargs["archived"] is False
        assert call_kwargs["table_db_id"] == 1
        assert call_kwargs["filter_items_in_personal_collection"] == "exclude"
        assert call_kwargs["verified"] is True


@pytest.mark.asyncio
async def test_search_resources_no_query_parameter(mock_context, sample_search_results):
    """Test search without a query parameter."""
    # Set up the mock
    client_mock = MagicMock()
    client_mock.search = AsyncMock(return_value={"results": sample_search_results, "pagination": {"page": 1, "page_size": 20, "total_count": 2, "total_pages": 1, "has_more": False}})
    
    with patch("supermetabase.tools.search.get_metabase_client", return_value=client_mock):
        # Call the tool without a query parameter
        result = await search_resources(
            ctx=mock_context,
            models=["dashboard"],
            created_by=[1]
        )
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert "results" in result_data
        assert len(result_data["results"]) == 2
        
        # Verify the mock was called with the correct parameters
        client_mock.search.assert_called_once()
        call_kwargs = client_mock.search.call_args[1]
        assert call_kwargs["query"] is None
        assert call_kwargs["models"] == ["dashboard"]
        assert call_kwargs["created_by"] == [1]


@pytest.mark.asyncio
async def test_search_resources_error(mock_context):
    """Test search with an error."""
    # Set up the mock to raise an exception
    client_mock = MagicMock()
    client_mock.search = AsyncMock(side_effect=ValueError("Test error"))
    
    with patch("supermetabase.tools.search.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await search_resources(ctx=mock_context, q="test")
        
        # Verify the result is an error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["message"] == "Test error"
        assert result_data["error"]["error_type"] == "search_error"


@pytest.mark.asyncio
async def test_search_resources_with_timestamp_filters(mock_context, sample_search_results):
    """Test search with timestamp filters."""
    # Set up the mock
    client_mock = MagicMock()
    client_mock.search = AsyncMock(return_value={"results": sample_search_results, "pagination": {"page": 1, "page_size": 20, "total_count": 2, "total_pages": 1, "has_more": False}})
    
    with patch("supermetabase.tools.search.get_metabase_client", return_value=client_mock):
        # Call the tool with timestamp filters
        result = await search_resources(
            ctx=mock_context,
            q="test",
            created_at="2023-01-01T00:00:00Z",
            last_edited_at="2023-01-02T00:00:00Z"
        )
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert "results" in result_data
        assert len(result_data["results"]) == 2
        
        # Verify the mock was called with the correct parameters
        client_mock.search.assert_called_once()
        call_kwargs = client_mock.search.call_args[1]
        assert call_kwargs["created_at"] == "2023-01-01T00:00:00Z"
        assert call_kwargs["last_edited_at"] == "2023-01-02T00:00:00Z"


@pytest.mark.asyncio
async def test_search_resources_with_dashboard_questions(mock_context, sample_search_results):
    """Test search including dashboard questions."""
    # Set up the mock
    client_mock = MagicMock()
    client_mock.search = AsyncMock(return_value={"results": sample_search_results, "pagination": {"page": 1, "page_size": 20, "total_count": 2, "total_pages": 1, "has_more": False}})
    
    with patch("supermetabase.tools.search.get_metabase_client", return_value=client_mock):
        # Call the tool with include_dashboard_questions
        result = await search_resources(
            ctx=mock_context,
            q="test",
            include_dashboard_questions=True
        )
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert "results" in result_data
        assert len(result_data["results"]) == 2
        
        # Verify the mock was called with the correct parameters
        client_mock.search.assert_called_once()
        call_kwargs = client_mock.search.call_args[1]
        assert call_kwargs["include_dashboard_questions"] is True


@pytest.mark.asyncio
async def test_search_resources_pagination(mock_context, sample_search_results_paginated):
    """Test search with pagination."""
    # Set up the mock to return paginated results
    client_mock = MagicMock()
    
    # We'll simulate client pagination here since we're modifying the client method to handle pagination
    async def mock_search(**kwargs):
        page = kwargs.get('page', 1)
        page_size = kwargs.get('page_size', 50)
        all_results = sample_search_results_paginated
        
        total_count = len(all_results)
        total_pages = (total_count + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_count)
        
        paginated_results = all_results[start_idx:end_idx]
        
        return {
            "results": paginated_results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_more": page < total_pages
            }
        }
    
    client_mock.search = AsyncMock(side_effect=mock_search)
    
    with patch("supermetabase.tools.search.get_metabase_client", return_value=client_mock):
        # Test first page
        result = await search_resources(ctx=mock_context, q="test", page=1, page_size=20)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check pagination metadata
        assert "pagination" in result_data
        assert result_data["pagination"]["page"] == 1
        assert result_data["pagination"]["page_size"] == 20
        assert result_data["pagination"]["total_count"] == 100
        assert result_data["pagination"]["total_pages"] == 5
        assert result_data["pagination"]["has_more"] == True
        
        # Check results
        assert "results" in result_data
        assert len(result_data["results"]) == 20
        
        # Test second page
        result2 = await search_resources(ctx=mock_context, q="test", page=2, page_size=20)
        result_data2 = json.loads(result2)
        
        # Check that we got the second page
        assert result_data2["pagination"]["page"] == 2
        assert len(result_data2["results"]) == 20
        assert result_data2["results"][0]["id"] == 21  # First result on second page
        
        # Test last page
        result5 = await search_resources(ctx=mock_context, q="test", page=5, page_size=20)
        result_data5 = json.loads(result5)
        
        # Check last page
        assert result_data5["pagination"]["page"] == 5
        assert result_data5["pagination"]["has_more"] == False
        assert len(result_data5["results"]) == 20