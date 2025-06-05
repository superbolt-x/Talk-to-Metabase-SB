"""
Test chart type validation in card tools.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

# Mock the FastMCP Context for testing
@pytest.fixture
def mock_context():
    """Create a mock MCP context for testing."""
    context = MagicMock()
    context.request_context.lifespan_context.auth.config.response_size_limit = 100000
    return context

@pytest.mark.asyncio
async def test_create_card_invalid_display_type(mock_context):
    """Test create_card with invalid display type."""
    from talk_to_metabase.tools.card import create_card
    
    # Test with invalid display type
    result = await create_card(
        database_id=1,
        query="SELECT 1",
        name="Test Card",
        ctx=mock_context,
        display="invalid_chart_type"
    )
    
    # Parse the JSON response
    response_data = json.loads(result)
    
    assert response_data["success"] is False
    assert "Invalid display type" in response_data["error"]
    assert "table, bar, line, combo" in response_data["error"]

@pytest.mark.asyncio 
async def test_update_card_invalid_display_type(mock_context):
    """Test update_card with invalid display type."""
    from talk_to_metabase.tools.card import update_card
    
    # Test with invalid display type
    result = await update_card(
        id=1,
        ctx=mock_context,
        display="invalid_chart_type"
    )
    
    # Parse the JSON response
    response_data = json.loads(result)
    
    assert response_data["success"] is False
    assert "Invalid display type" in response_data["error"]
    assert "table, bar, line, combo" in response_data["error"]

@pytest.mark.asyncio
async def test_create_card_valid_display_types(mock_context):
    """Test create_card with valid display types."""
    from talk_to_metabase.tools.card import create_card
    
    valid_types = ["table", "bar", "line", "combo"]
    
    for display_type in valid_types:
        with patch('talk_to_metabase.tools.card.get_metabase_client') as mock_client_getter:
            # Mock the client and execution result
            mock_client = MagicMock()
            mock_client_getter.return_value = mock_client
            
            # Mock successful query execution
            with patch('talk_to_metabase.tools.card.execute_sql_query') as mock_execute:
                mock_execute.return_value = {"success": True, "result_metadata": []}
                
                # Mock successful card creation
                mock_client.auth.make_request = AsyncMock(return_value=(
                    {"id": 123, "name": "Test Card"}, 200, None
                ))
                
                result = await create_card(
                    database_id=1,
                    query="SELECT 1",
                    name="Test Card",
                    ctx=mock_context,
                    display=display_type
                )
                
                # Parse the JSON response
                response_data = json.loads(result)
                
                # Should not fail on display type validation
                if response_data.get("success") is False:
                    assert "Invalid display type" not in response_data.get("error", "")
