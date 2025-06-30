"""
Resource management utility for Talk to Metabase MCP server.

This module provides functions to load JSON schemas and documentation files
that work correctly in both development and PyInstaller bundled environments.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def get_resource_path(relative_path: str) -> Path:
    """
    Get the absolute path to a resource file.
    
    This function works correctly in both development and PyInstaller bundled environments.
    
    Args:
        relative_path: Path relative to the talk_to_metabase package
        
    Returns:
        Absolute path to the resource
    """
    try:
        # Check if we're in a PyInstaller bundle
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running in a PyInstaller bundle
            # Files are bundled at _MEIPASS/talk_to_metabase/schemas/...
            base_path = Path(sys._MEIPASS) / 'talk_to_metabase'
        else:
            # Running in development
            # Files are at talk_to_metabase/schemas/... relative to this file
            base_path = Path(__file__).parent
        
        resource_path = base_path / relative_path
        return resource_path
    except Exception as e:
        logger.error(f"Error resolving resource path for {relative_path}: {e}")
        # Fallback to current directory approach
        fallback_path = Path(__file__).parent / relative_path
        return fallback_path


def load_json_resource(relative_path: str) -> Optional[Dict[str, Any]]:
    """
    Load a JSON resource file.
    
    Args:
        relative_path: Path to JSON file relative to talk_to_metabase package
        
    Returns:
        Parsed JSON data or None if loading fails
    """
    try:
        resource_path = get_resource_path(relative_path)
        
        if not resource_path.exists():
            logger.error(f"JSON resource file not found: {resource_path}")
            return None
        
        with open(resource_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        logger.error(f"Error loading JSON resource {relative_path}: {e}")
        return None


def load_text_resource(relative_path: str) -> Optional[str]:
    """
    Load a text resource file.
    
    Args:
        relative_path: Path to text file relative to talk_to_metabase package
        
    Returns:
        File contents as string or None if loading fails
    """
    try:
        resource_path = get_resource_path(relative_path)
        
        if not resource_path.exists():
            logger.error(f"Text resource file not found: {resource_path}")
            return None
        
        with open(resource_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content
    except Exception as e:
        logger.error(f"Error loading text resource {relative_path}: {e}")
        return None


def list_resource_directory(relative_path: str) -> list:
    """
    List files in a resource directory.
    
    Args:
        relative_path: Path to directory relative to talk_to_metabase package
        
    Returns:
        List of filenames in the directory
    """
    try:
        resource_path = get_resource_path(relative_path)
        
        if not resource_path.exists() or not resource_path.is_dir():
            logger.error(f"Resource directory not found: {resource_path}")
            return []
        
        files = [f.name for f in resource_path.iterdir() if f.is_file()]
        return files
    except Exception as e:
        logger.error(f"Error listing resource directory {relative_path}: {e}")
        return []


# Schema-specific convenience functions
def load_visualization_schema(chart_type: str) -> Optional[Dict[str, Any]]:
    """Load JSON schema for a specific chart type."""
    schema_path = f"schemas/{chart_type}_visualization.json"
    schema = load_json_resource(schema_path)
    if schema is None:
        logger.error(f"Failed to load {schema_path}")
        # Debug: try to list what's actually available
        try:
            available_files = list_resource_directory("schemas")
            logger.error(f"Available schema files: {available_files}")
        except Exception as e:
            logger.error(f"Could not list schema directory: {e}")
    return schema


def load_visualization_docs(chart_type: str) -> Optional[str]:
    """Load documentation for a specific chart type."""
    docs_path = f"schemas/{chart_type}_visualization_docs.md"
    return load_text_resource(docs_path)


def load_parameters_schema() -> Optional[Dict[str, Any]]:
    """Load the parameters JSON schema."""
    schema = load_json_resource("schemas/parameters.json")
    if schema is None:
        logger.error("Failed to load parameters.json schema file")
        # Debug: try to list what's actually available
        try:
            available_files = list_resource_directory("schemas")
            logger.error(f"Available schema files: {available_files}")
        except Exception as e:
            logger.error(f"Could not list schema directory: {e}")
    return schema


def load_dashcards_schema() -> Optional[Dict[str, Any]]:
    """Load the dashcards JSON schema."""
    return load_json_resource("schemas/dashcards.json")


def load_card_parameters_schema() -> Optional[Dict[str, Any]]:
    """Load the card parameters JSON schema."""
    return load_json_resource("schemas/card_parameters.json")


def load_card_parameters_docs() -> Optional[str]:
    """Load the card parameters documentation."""
    return load_text_resource("schemas/card_parameters_docs.md")


def load_dashboard_parameters_schema() -> Optional[Dict[str, Any]]:
    """Load the dashboard parameters JSON schema."""
    return load_json_resource("schemas/dashboard_parameters.json")


def load_dashboard_parameters_docs() -> Optional[str]:
    """Load the dashboard parameters documentation."""
    return load_text_resource("schemas/dashboard_parameters_docs.md")
