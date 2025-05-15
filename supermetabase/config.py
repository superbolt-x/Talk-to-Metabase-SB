"""
Configuration module for the SuperMetabase MCP Server.
"""

import os
from typing import Dict, Optional

from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()


class MetabaseConfig(BaseModel):
    """Configuration for Metabase connection."""

    url: str = Field(..., description="Base URL of the Metabase instance")
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")
    session_token: Optional[str] = Field(None, description="Session token after authentication")
    response_size_limit: int = Field(100000, description="Maximum size in characters for responses sent to Claude")

    @validator("url")
    def validate_url(cls, v: str) -> str:
        """Ensure URL ends with a trailing slash."""
        if not v.endswith("/"):
            v = f"{v}/"
        return v

    @classmethod
    def from_env(cls) -> "MetabaseConfig":
        """Create a configuration instance from environment variables."""
        # Get the response size limit with a default value if not set
        try:
            response_size_limit = int(os.environ.get("RESPONSE_SIZE_LIMIT", "100000"))
        except ValueError:
            response_size_limit = 100000
            
        return cls(
            url=os.environ.get("METABASE_URL", ""),
            username=os.environ.get("METABASE_USERNAME", ""),
            password=os.environ.get("METABASE_PASSWORD", ""),
            response_size_limit=response_size_limit,
        )
