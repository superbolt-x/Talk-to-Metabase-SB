"""
Unit tests for visualization tools.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from talk_to_metabase.tools.visualization import (
    get_visualization_docs_for_types,
    validate_visualization_settings,
    get_validation_notes
)


class TestVisualizationDocumentation:
    """Test visualization documentation functionality."""
    
    def test_get_docs_for_valid_types(self):
        """Test getting documentation for valid chart types."""
        chart_types = ["table", "bar", "line"]
        docs = get_visualization_docs_for_types(chart_types)
        
        assert "common_settings" in docs
        assert "chart_specific" in docs
        assert docs["requested_types"] == chart_types
        assert docs["invalid_types"] == []
        
        # Check that all requested types are in chart_specific
        for chart_type in chart_types:
            assert chart_type in docs["chart_specific"]
            assert "description" in docs["chart_specific"][chart_type]
            assert "settings" in docs["chart_specific"][chart_type]
            assert "example" in docs["chart_specific"][chart_type]
    
    def test_get_docs_for_invalid_types(self):
        """Test getting documentation for invalid chart types."""
        chart_types = ["invalid_type", "bar"]
        docs = get_visualization_docs_for_types(chart_types)
        
        assert docs["requested_types"] == ["bar"]
        assert docs["invalid_types"] == ["invalid_type"]
        assert "bar" in docs["chart_specific"]
        assert "invalid_type" not in docs["chart_specific"]
    
    def test_get_docs_for_combo_chart(self):
        """Test getting documentation for combo chart."""
        chart_types = ["combo"]
        docs = get_visualization_docs_for_types(chart_types)
        
        combo_doc = docs["chart_specific"]["combo"]
        assert "series_settings" in combo_doc["settings"]
        assert "display" in combo_doc["settings"]["series_settings"]["properties"]
        assert "axis" in combo_doc["settings"]["series_settings"]["properties"]


class TestVisualizationValidation:
    """Test visualization settings validation."""
    
    def test_validate_bar_chart_valid(self):
        """Test validation of valid bar chart settings."""
        settings = {
            "graph.dimensions": ["Category"],
            "graph.metrics": ["Revenue"],
            "graph.show_values": True,
            "series_settings": {
                "Revenue": {
                    "color": "#509EE3"
                }
            }
        }
        
        is_valid, errors = validate_visualization_settings(settings, "bar")
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_bar_chart_missing_dimensions(self):
        """Test validation of bar chart missing required dimensions."""
        settings = {
            "graph.metrics": ["Revenue"]
        }
        
        is_valid, errors = validate_visualization_settings(settings, "bar")
        assert not is_valid
        assert any("graph.dimensions" in error for error in errors)
    
    def test_validate_bar_chart_missing_metrics(self):
        """Test validation of bar chart missing required metrics."""
        settings = {
            "graph.dimensions": ["Category"]
        }
        
        is_valid, errors = validate_visualization_settings(settings, "bar")
        assert not is_valid
        assert any("graph.metrics" in error for error in errors)
    
    def test_validate_combo_chart_valid(self):
        """Test validation of valid combo chart settings."""
        settings = {
            "graph.dimensions": ["Date"],
            "graph.metrics": ["Revenue", "Orders"],
            "series_settings": {
                "Revenue": {
                    "display": "bar",
                    "axis": "left",
                    "color": "#509EE3"
                },
                "Orders": {
                    "display": "line",
                    "axis": "right",
                    "color": "#88BF4D"
                }
            }
        }
        
        is_valid, errors = validate_visualization_settings(settings, "combo")
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_combo_chart_missing_series_settings(self):
        """Test validation of combo chart missing series_settings."""
        settings = {
            "graph.dimensions": ["Date"],
            "graph.metrics": ["Revenue"]
        }
        
        is_valid, errors = validate_visualization_settings(settings, "combo")
        assert not is_valid
        assert any("series_settings" in error for error in errors)
    
    def test_validate_combo_chart_invalid_series_display(self):
        """Test validation of combo chart with invalid series display."""
        settings = {
            "graph.dimensions": ["Date"],
            "graph.metrics": ["Revenue"],
            "series_settings": {
                "Revenue": {
                    "display": "invalid_display",
                    "axis": "left"
                }
            }
        }
        
        is_valid, errors = validate_visualization_settings(settings, "combo")
        assert not is_valid
        assert any("display type must be" in error for error in errors)
    
    def test_validate_combo_chart_missing_series_axis(self):
        """Test validation of combo chart missing series axis."""
        settings = {
            "graph.dimensions": ["Date"],
            "graph.metrics": ["Revenue"],
            "series_settings": {
                "Revenue": {
                    "display": "bar"
                    # Missing axis
                }
            }
        }
        
        is_valid, errors = validate_visualization_settings(settings, "combo")
        assert not is_valid
        assert any("must specify 'axis'" in error for error in errors)
    
    def test_validate_invalid_color_format(self):
        """Test validation of invalid color format."""
        settings = {
            "graph.dimensions": ["Category"],
            "graph.metrics": ["Revenue"],
            "series_settings": {
                "Revenue": {
                    "color": "invalid_color"
                }
            }
        }
        
        is_valid, errors = validate_visualization_settings(settings, "bar")
        assert not is_valid
        assert any("color must be a hex code" in error for error in errors)
    
    def test_validate_valid_color_format(self):
        """Test validation of valid color formats."""
        settings = {
            "graph.dimensions": ["Category"],
            "graph.metrics": ["Revenue"],
            "series_settings": {
                "Revenue": {
                    "color": "#509EE3"  # Valid hex
                }
            }
        }
        
        is_valid, errors = validate_visualization_settings(settings, "bar")
        assert is_valid
        assert len(errors) == 0
        
        # Test valid color name
        settings["series_settings"]["Revenue"]["color"] = "brand"
        is_valid, errors = validate_visualization_settings(settings, "bar")
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_invalid_boolean_field(self):
        """Test validation of invalid boolean field."""
        settings = {
            "graph.dimensions": ["Category"],
            "graph.metrics": ["Revenue"],
            "graph.show_values": "true"  # Should be boolean, not string
        }
        
        is_valid, errors = validate_visualization_settings(settings, "bar")
        assert not is_valid
        assert any("must be a boolean" in error for error in errors)
    
    def test_validate_invalid_numeric_field(self):
        """Test validation of invalid numeric field."""
        settings = {
            "graph.dimensions": ["Category"],
            "graph.metrics": ["Revenue"],
            "graph.y_axis.min": "0"  # Should be number, not string
        }
        
        is_valid, errors = validate_visualization_settings(settings, "bar")
        assert not is_valid
        assert any("must be a number" in error for error in errors)
    
    def test_validate_line_chart_valid(self):
        """Test validation of valid line chart settings."""
        settings = {
            "graph.dimensions": ["Date"],
            "graph.metrics": ["Revenue"],
            "graph.x_axis.scale": "timeseries",
            "series_settings": {
                "Revenue": {
                    "line.interpolate": "linear",
                    "line.marker_enabled": True
                }
            }
        }
        
        is_valid, errors = validate_visualization_settings(settings, "line")
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_invalid_axis_scale(self):
        """Test validation of invalid axis scale."""
        settings = {
            "graph.dimensions": ["Category"],
            "graph.metrics": ["Revenue"],
            "graph.x_axis.scale": "invalid_scale"
        }
        
        is_valid, errors = validate_visualization_settings(settings, "bar")
        assert not is_valid
        assert any("Invalid graph.x_axis.scale" in error for error in errors)
    
    def test_validate_table_chart_valid(self):
        """Test validation of valid table settings."""
        settings = {
            "column_settings": {
                "[\"name\",\"Revenue\"]": {
                    "number_style": "currency",
                    "currency": "USD"
                }
            }
        }
        
        is_valid, errors = validate_visualization_settings(settings, "table")
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_table_invalid_column_settings(self):
        """Test validation of invalid table column_settings."""
        settings = {
            "column_settings": "not_an_object"
        }
        
        is_valid, errors = validate_visualization_settings(settings, "table")
        assert not is_valid
        assert any("column_settings must be an object" in error for error in errors)
    
    def test_get_validation_notes(self):
        """Test that validation notes are returned."""
        notes = get_validation_notes()
        assert isinstance(notes, list)
        assert len(notes) > 0
        assert any("Field references must use exact format" in note for note in notes)
        assert any("Color values must be hex codes" in note for note in notes)
