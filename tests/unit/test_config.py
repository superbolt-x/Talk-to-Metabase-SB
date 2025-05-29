"""
Tests for configuration module.
"""

import os
from unittest.mock import patch

import pytest

from talk_to_metabase.config import MetabaseConfig


def test_validate_url():
    """Test URL validation."""
    # Without trailing slash
    config = MetabaseConfig(
        url="https://metabase.example.com", 
        username="test@example.com",
        password="password123"
    )
    assert config.url == "https://metabase.example.com/"
    
    # With trailing slash
    config = MetabaseConfig(
        url="https://metabase.example.com/", 
        username="test@example.com",
        password="password123"
    )
    assert config.url == "https://metabase.example.com/"


def test_from_env():
    """Test creating config from environment variables."""
    env_vars = {
        "METABASE_URL": "https://env-metabase.example.com",
        "METABASE_USERNAME": "env-user@example.com",
        "METABASE_PASSWORD": "env-password"
    }
    
    with patch.dict(os.environ, env_vars):
        config = MetabaseConfig.from_env()
        
        assert config.url == "https://env-metabase.example.com/"
        assert config.username == "env-user@example.com"
        assert config.password == "env-password"
        assert config.session_token is None
