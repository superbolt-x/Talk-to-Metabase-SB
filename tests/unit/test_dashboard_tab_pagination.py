"""
Additional tests for the paginated get_dashboard_tab functionality.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from talk_to_metabase.tools.dashboard import get_dashboard_tab


@pytest.mark.asyncio
async def test_get_dashboard_tab_with_pagination(mock_context, sample_dashboard, sample_card):
    """Test dashboard tab retrieval with pagination."""
    # Create a dashboard with many cards to test pagination
    dashboard_with_many_cards = sample_dashboard.copy()
    dashboard_with_many_cards["dashcards"] = []
    
    # Create 30 test cards (exceeding the default page size of 20)
    for i in range(30):
        # Create cards in a grid, 5 columns per row
        row = i // 5
        col = i % 5
        
        dashcard = {
            "id": i + 1,
            "dashboard_id": 1,
            "card_id": i + 1,
            "size_x": 4,
            "size_y": 2,
            "row": row,
            "col": col * 4,  # Space them out evenly
            "card": sample_card.copy(),
            "series": []
        }
        # Modify some properties to make each card unique
        dashcard["card"]["id"] = i + 1
        dashcard["card"]["name"] = f"Test Card {i + 1}"
        
        dashboard_with_many_cards["dashcards"].append(dashcard)
    
    # Set up the mock
    client_mock = MagicMock()
    client_mock.get_resource = AsyncMock(return_value=dashboard_with_many_cards)
    
    with patch("talk_to_metabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool with default pagination (page 1, page_size 20)
        result = await get_dashboard_tab(dashboard_id=1, ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check pagination metadata
        assert "pagination" in result_data
        assert result_data["pagination"]["page"] == 1
        assert result_data["pagination"]["page_size"] == 20
        assert result_data["pagination"]["total_cards"] == 30
        assert result_data["pagination"]["total_pages"] == 2
        assert result_data["pagination"]["has_more"] is True
        assert "note" in result_data["pagination"]
        
        # Check that only 20 cards were returned
        assert len(result_data["dashcards"]) == 20
        
        # Verify that rows are sorted correctly (top to bottom, left to right)
        for i in range(1, len(result_data["dashcards"])):
            prev_card = result_data["dashcards"][i-1]
            curr_card = result_data["dashcards"][i]
            
            # Either the current card is on a later row, or on the same row but further right
            assert (curr_card["row"] > prev_card["row"]) or \
                   (curr_card["row"] == prev_card["row"] and curr_card["col"] > prev_card["col"])


@pytest.mark.asyncio
async def test_get_dashboard_tab_pagination_second_page(mock_context, sample_dashboard, sample_card):
    """Test dashboard tab retrieval with pagination - getting the second page."""
    # Create a dashboard with many cards to test pagination
    dashboard_with_many_cards = sample_dashboard.copy()
    dashboard_with_many_cards["dashcards"] = []
    
    # Create 30 test cards (exceeding the default page size of 20)
    for i in range(30):
        # Create cards in a grid, 5 columns per row
        row = i // 5
        col = i % 5
        
        dashcard = {
            "id": i + 1,
            "dashboard_id": 1,
            "card_id": i + 1,
            "size_x": 4,
            "size_y": 2,
            "row": row,
            "col": col * 4,  # Space them out evenly
            "card": sample_card.copy(),
            "series": []
        }
        # Modify some properties to make each card unique
        dashcard["card"]["id"] = i + 1
        dashcard["card"]["name"] = f"Test Card {i + 1}"
        
        dashboard_with_many_cards["dashcards"].append(dashcard)
    
    # Set up the mock
    client_mock = MagicMock()
    client_mock.get_resource = AsyncMock(return_value=dashboard_with_many_cards)
    
    with patch("talk_to_metabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool for the second page
        result = await get_dashboard_tab(dashboard_id=1, ctx=mock_context, page=2)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check pagination metadata
        assert "pagination" in result_data
        assert result_data["pagination"]["page"] == 2
        assert result_data["pagination"]["page_size"] == 20
        assert result_data["pagination"]["total_cards"] == 30
        assert result_data["pagination"]["total_pages"] == 2
        assert result_data["pagination"]["has_more"] is False
        
        # Check that 10 cards were returned (remainder after first page)
        assert len(result_data["dashcards"]) == 10
        
        # Check that the correct cards were returned (ID 21-30)
        card_ids = [card["card_summary"]["id"] for card in result_data["dashcards"]]
        assert min(card_ids) == 21
        assert max(card_ids) == 30


@pytest.mark.asyncio
async def test_get_dashboard_tab_custom_page_size(mock_context, sample_dashboard, sample_card):
    """Test dashboard tab retrieval with custom page size."""
    # Create a dashboard with many cards to test pagination
    dashboard_with_many_cards = sample_dashboard.copy()
    dashboard_with_many_cards["dashcards"] = []
    
    # Create 30 test cards
    for i in range(30):
        # Create cards in a grid, 5 columns per row
        row = i // 5
        col = i % 5
        
        dashcard = {
            "id": i + 1,
            "dashboard_id": 1,
            "card_id": i + 1,
            "size_x": 4,
            "size_y": 2,
            "row": row,
            "col": col * 4,  # Space them out evenly
            "card": sample_card.copy(),
            "series": []
        }
        # Modify some properties to make each card unique
        dashcard["card"]["id"] = i + 1
        dashcard["card"]["name"] = f"Test Card {i + 1}"
        
        dashboard_with_many_cards["dashcards"].append(dashcard)
    
    # Set up the mock
    client_mock = MagicMock()
    client_mock.get_resource = AsyncMock(return_value=dashboard_with_many_cards)
    
    with patch("talk_to_metabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool with a custom page size of 10
        result = await get_dashboard_tab(dashboard_id=1, ctx=mock_context, page_size=10)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        # Check pagination metadata
        assert "pagination" in result_data
        assert result_data["pagination"]["page"] == 1
        assert result_data["pagination"]["page_size"] == 10
        assert result_data["pagination"]["total_cards"] == 30
        assert result_data["pagination"]["total_pages"] == 3
        assert result_data["pagination"]["has_more"] is True
        
        # Check that 10 cards were returned (per our custom page size)
        assert len(result_data["dashcards"]) == 10


@pytest.mark.asyncio
async def test_get_dashboard_tab_invalid_page(mock_context, sample_dashboard, sample_card):
    """Test error handling when requesting an invalid page."""
    # Create a dashboard with cards
    dashboard_with_cards = sample_dashboard.copy()
    dashboard_with_cards["dashcards"] = []
    
    # Add 5 cards
    for i in range(5):
        dashcard = {
            "id": i + 1,
            "dashboard_id": 1,
            "card_id": i + 1,
            "size_x": 4,
            "size_y": 2,
            "row": i,
            "col": 0,
            "card": sample_card.copy(),
            "series": []
        }
        dashboard_with_cards["dashcards"].append(dashcard)
    
    # Set up the mock
    client_mock = MagicMock()
    client_mock.get_resource = AsyncMock(return_value=dashboard_with_cards)
    
    with patch("talk_to_metabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool with an invalid page number (page=0)
        result_invalid_page = await get_dashboard_tab(dashboard_id=1, ctx=mock_context, page=0)
        
        # Verify the error response
        assert isinstance(result_invalid_page, str)
        result_data = json.loads(result_invalid_page)
        
        assert "success" in result_data
        assert result_data["success"] is False
        assert "error" in result_data
        assert result_data["error"]["error_type"] == "invalid_pagination"
        
        # Call the tool with a page that exceeds the total pages
        result_excess_page = await get_dashboard_tab(dashboard_id=1, ctx=mock_context, page=3)
        
        # Verify the error response
        assert isinstance(result_excess_page, str)
        result_data = json.loads(result_excess_page)
        
        assert "success" in result_data
        assert result_data["success"] is False
        assert "error" in result_data
        assert result_data["error"]["error_type"] == "page_out_of_range"


@pytest.mark.asyncio
async def test_get_dashboard_tab_invalid_page_size(mock_context, sample_dashboard):
    """Test error handling when using an invalid page size."""
    # Set up the mock
    client_mock = MagicMock()
    client_mock.get_resource = AsyncMock(return_value=sample_dashboard)
    
    with patch("talk_to_metabase.tools.dashboard.get_metabase_client", return_value=client_mock):
        # Call the tool with an invalid page size (page_size=0)
        result = await get_dashboard_tab(dashboard_id=1, ctx=mock_context, page_size=0)
        
        # Verify the error response
        assert isinstance(result, str)
        result_data = json.loads(result)
        
        assert "success" in result_data
        assert result_data["success"] is False
        assert "error" in result_data
        assert result_data["error"]["error_type"] == "invalid_pagination"
