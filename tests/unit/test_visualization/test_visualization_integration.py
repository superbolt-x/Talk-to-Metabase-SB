"""
Integration tests for visualization tools with MCP server.
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
async def test_get_visualization_document_tool(mock_context):
    """Test the GET_VISUALIZATION_DOCUMENT tool."""
    from talk_to_metabase.tools.visualization import get_visualization_document
    
    # Test with valid chart types
    result = await get_visualization_document(["bar", "line"], mock_context)
    
    # Parse the JSON response
    response_data = json.loads(result)
    
    assert response_data["success"] is True
    assert response_data["requested_types"] == ["bar", "line"]
    assert response_data["valid_types"] == ["bar", "line"]
    assert response_data["invalid_types"] == []
    assert "documentation" in response_data
    assert "common_settings" in response_data["documentation"]
    assert "chart_specific" in response_data["documentation"]
    assert "bar" in response_data["documentation"]["chart_specific"]
    assert "line" in response_data["documentation"]["chart_specific"]
    assert "validation_notes" in response_data


@pytest.mark.asyncio
async def test_get_visualization_document_invalid_types(mock_context):
    """Test the GET_VISUALIZATION_DOCUMENT tool with invalid types."""
    from talk_to_metabase.tools.visualization import get_visualization_document
    
    # Test with mix of valid and invalid chart types
    result = await get_visualization_document(["bar", "invalid_type"], mock_context)
    
    # Parse the JSON response
    response_data = json.loads(result)
    
    assert response_data["success"] is True
    assert response_data["requested_types"] == ["bar", "invalid_type"]
    assert response_data["valid_types"] == ["bar"]
    assert response_data["invalid_types"] == ["invalid_type"]
    assert "warning" in response_data


@pytest.mark.asyncio
async def test_get_visualization_document_empty_list(mock_context):
    """Test the GET_VISUALIZATION_DOCUMENT tool with empty list."""
    from talk_to_metabase.tools.visualization import get_visualization_document
    
    # Test with empty list
    result = await get_visualization_document([], mock_context)
    
    # Parse the JSON response
    response_data = json.loads(result)
    
    assert response_data["success"] is False
    assert "error_type" in response_data
    assert "invalid_parameter" in response_data["error_type"]


class TestVisualizationDocumentationContent:
    """Test the content and structure of visualization documentation."""
    
    def test_bar_chart_documentation_completeness(self):
        """Test that bar chart documentation has all required fields."""
        from talk_to_metabase.tools.visualization import get_visualization_docs_for_types
        
        docs = get_visualization_docs_for_types(["bar"])
        bar_doc = docs["chart_specific"]["bar"]
        
        # Check essential settings are documented
        settings = bar_doc["settings"]
        assert "graph.dimensions" in settings
        assert "graph.metrics" in settings
        assert "series_settings" in settings
        assert "stackable.stack_type" in settings
        
        # Check example is complete
        example = bar_doc["example"]
        assert "graph.dimensions" in example
        assert "graph.metrics" in example
        assert "series_settings" in example
    
    def test_combo_chart_documentation_completeness(self):
        """Test that combo chart documentation emphasizes required fields."""
        from talk_to_metabase.tools.visualization import get_visualization_docs_for_types
        
        docs = get_visualization_docs_for_types(["combo"])
        combo_doc = docs["chart_specific"]["combo"]
        
        # Check that series_settings is well documented
        series_settings = combo_doc["settings"]["series_settings"]
        assert "KEY REQUIREMENT" in series_settings["description"]
        assert "display" in series_settings["properties"]
        assert "axis" in series_settings["properties"]
        
        # Check example shows multiple series with different chart types
        example = combo_doc["example"]
        assert "series_settings" in example
        series_in_example = example["series_settings"]
        
        # Should have at least one bar and one line series
        display_types = [series["display"] for series in series_in_example.values()]
        assert "bar" in display_types
        assert "line" in display_types
    
    def test_common_settings_documentation(self):
        """Test that common settings are properly documented."""
        from talk_to_metabase.tools.visualization import get_visualization_docs_for_types
        
        docs = get_visualization_docs_for_types(["table"])
        common_settings = docs["common_settings"]["settings"]
        
        # Check essential common settings
        assert "card.title" in common_settings
        assert "card.description" in common_settings
        assert "click_behavior" in common_settings
        
        # Check click_behavior is well documented
        click_behavior = common_settings["click_behavior"]
        assert "properties" in click_behavior
        assert "type" in click_behavior["properties"]
        assert "linkType" in click_behavior["properties"]
