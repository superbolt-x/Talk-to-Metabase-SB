"""
Tests for authentication module.
"""

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from talk_to_metabase.auth import MetabaseAuth
from talk_to_metabase.config import MetabaseConfig


@pytest.fixture
def config():
    """Create a test configuration."""
    return MetabaseConfig(
        url="https://test-metabase.example.com/", 
        username="test@example.com",
        password="password123"
    )


@pytest.mark.asyncio
async def test_authenticate_success(config):
    """Test successful authentication."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "test-session-token"}
    
    # Mock the HTTP client post method
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        auth = MetabaseAuth(config)
        result = await auth.authenticate()
        
        assert result is True
        assert auth.session_token == "test-session-token"
        assert auth.client.headers.get("X-Metabase-Session") == "test-session-token"


@pytest.mark.asyncio
async def test_authenticate_failure(config):
    """Test failed authentication."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Authentication failed"
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "{", 0)
    
    # Mock the HTTP client post method
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        auth = MetabaseAuth(config)
        result = await auth.authenticate()
        
        assert result is False
        assert auth.session_token is None


@pytest.mark.asyncio
async def test_ensure_authenticated_existing_token(config):
    """Test ensure_authenticated with existing valid token."""
    # Create auth with an existing token
    config.session_token = "existing-token"
    auth = MetabaseAuth(config)
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    
    # Mock the HTTP client get method
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await auth.ensure_authenticated()
        
        assert result is True
        assert auth.session_token == "existing-token"


@pytest.mark.asyncio
async def test_ensure_authenticated_expired_token(config):
    """Test ensure_authenticated with expired token."""
    # Create auth with an existing token
    config.session_token = "expired-token"
    auth = MetabaseAuth(config)
    
    mock_get_response = MagicMock()
    mock_get_response.status_code = 401
    
    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = {"id": "new-session-token"}
    
    # Mock the HTTP client methods
    with patch("httpx.AsyncClient.get", return_value=mock_get_response), \
         patch("httpx.AsyncClient.post", return_value=mock_post_response):
        
        result = await auth.ensure_authenticated()
        
        assert result is True
        assert auth.session_token == "new-session-token"


@pytest.mark.asyncio
async def test_make_request_success(config):
    """Test make_request with successful request."""
    auth = MetabaseAuth(config)
    auth.ensure_authenticated = AsyncMock(return_value=True)
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test-data"}
    
    # Mock the HTTP client methods
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        data, status, error = await auth.make_request("GET", "test/endpoint")
        
        assert data == {"data": "test-data"}
        assert status == 200
        assert error is None


@pytest.mark.asyncio
async def test_make_request_error(config):
    """Test make_request with error response."""
    auth = MetabaseAuth(config)
    auth.ensure_authenticated = AsyncMock(return_value=True)
    
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"message": "Resource not found"}
    
    # Mock the HTTP client methods
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        data, status, error = await auth.make_request("GET", "test/endpoint")
        
        assert data == {"message": "Resource not found"}
        assert status == 404
        assert error == "Resource not found"


@pytest.mark.asyncio
async def test_make_request_auth_failure(config):
    """Test make_request with authentication failure."""
    auth = MetabaseAuth(config)
    auth.ensure_authenticated = AsyncMock(return_value=False)
    
    data, status, error = await auth.make_request("GET", "test/endpoint")
    
    assert data is None
    assert status == 401
    assert error == "Authentication failed"
