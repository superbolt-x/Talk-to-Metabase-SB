"""
Pytest fixtures for testing.
"""

import json
import os
from typing import Dict, Any

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from talk_to_metabase.auth import MetabaseAuth
from talk_to_metabase.client import MetabaseClient
from talk_to_metabase.config import MetabaseConfig
from talk_to_metabase.server import MetabaseContext


@pytest.fixture
def config():
    """Create a test configuration."""
    return MetabaseConfig(
        url="https://test-metabase.example.com/", 
        username="test@example.com",
        password="password123"
    )


@pytest.fixture
def mock_auth(config):
    """Create a mocked authentication client."""
    auth = MetabaseAuth(config)
    auth.session_token = "test-session-token"
    auth.client.headers["X-Metabase-Session"] = "test-session-token"
    
    # Mock the make_request method
    async def mock_make_request(method, path, **kwargs):
        """Mock implementation of make_request."""
        # Default to successful response
        return {"success": True, "data": "test-data"}, 200, None
    
    auth.make_request = AsyncMock(side_effect=mock_make_request)
    return auth


@pytest.fixture
def mock_metabase_client(mock_auth):
    """Create a mocked Metabase client."""
    return MetabaseClient(mock_auth)


@pytest.fixture
def mock_context(mock_auth):
    """Create a mocked MCP context."""
    context = MagicMock()
    context.request_context = MagicMock()
    context.request_context.lifespan_context = MetabaseContext(auth=mock_auth)
    return context


@pytest.fixture
def sample_dashboard() -> Dict[str, Any]:
    """Sample dashboard data."""
    return {
        "id": 1,
        "name": "Test Dashboard",
        "description": "A test dashboard",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-02T00:00:00Z",
        "collection_id": 1,
        "creator_id": 1,
        "parameters": [],
        "ordered_cards": []
    }


@pytest.fixture
def sample_card() -> Dict[str, Any]:
    """Sample card data."""
    return {
        "id": 1,
        "name": "Test Card",
        "description": "A test card",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-02T00:00:00Z",
        "collection_id": 1,
        "creator_id": 1,
        "database_id": 1,
        "table_id": 1,
        "dataset_query": {
            "type": "query",
            "database": 1,
            "query": {
                "source-table": 1
            }
        },
        "display": "table",
        "visualization_settings": {}
    }


@pytest.fixture
def sample_collection() -> Dict[str, Any]:
    """Sample collection data."""
    return {
        "id": 1,
        "name": "Test Collection",
        "description": "A test collection",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-02T00:00:00Z",
        "color": "#509EE3",
        "parent_id": None,
        "namespace": "default"
    }


@pytest.fixture
def sample_database() -> Dict[str, Any]:
    """Sample database data."""
    return {
        "id": 1,
        "name": "Test Database",
        "description": "A test database",
        "engine": "postgres",
        "features": ["basic-aggregations", "standard-deviation-aggregations"],
        "is_sample": False,
        "is_on_demand": False,
        "tables": []
    }
