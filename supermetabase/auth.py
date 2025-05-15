"""
Authentication module for Metabase API.
"""

import json
import logging
from typing import Dict, Optional, Tuple

import httpx

from .config import MetabaseConfig

logger = logging.getLogger(__name__)


class MetabaseAuth:
    """Handles authentication with the Metabase API."""

    def __init__(self, config: MetabaseConfig):
        """Initialize with Metabase configuration."""
        self.config = config
        self.session_token = config.session_token
        self.client = httpx.AsyncClient(base_url=config.url, timeout=30.0)

    async def ensure_authenticated(self) -> bool:
        """Ensure we have a valid session token, authenticating if needed."""
        if not self.session_token:
            return await self.authenticate()
        
        # Test if the token is still valid
        try:
            self.client.headers.update({"X-Metabase-Session": self.session_token})
            response = await self.client.get("api/user/current")
            if response.status_code == 200:
                return True
            
            # If not valid, authenticate again
            return await self.authenticate()
        except Exception as e:
            logger.error(f"Error testing authentication: {e}")
            return await self.authenticate()

    async def authenticate(self) -> bool:
        """Authenticate with Metabase and store the session token."""
        try:
            response = await self.client.post(
                "api/session",
                json={
                    "username": self.config.username,
                    "password": self.config.password,
                },
            )
            
            if response.status_code != 200:
                logger.error(
                    f"Authentication failed with status code {response.status_code}: {response.text}"
                )
                return False
            
            data = response.json()
            self.session_token = data.get("id")
            
            if not self.session_token:
                logger.error(f"Session token not found in response: {data}")
                return False
            
            # Update the client headers with the new session token
            self.client.headers.update({"X-Metabase-Session": self.session_token})
            self.config.session_token = self.session_token
            return True
        
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def make_request(
        self, method: str, path: str, **kwargs
    ) -> Tuple[Optional[Dict], int, Optional[str]]:
        """
        Make an authenticated request to the Metabase API.
        
        Returns:
            Tuple of (response_data, status_code, error_message)
        """
        if not await self.ensure_authenticated():
            return None, 401, "Authentication failed"

        try:
            method_func = getattr(self.client, method.lower())
            response = await method_func(f"api/{path.lstrip('/')}", **kwargs)
            
            if response.status_code == 401:
                # Token might have expired, try to authenticate again
                if await self.authenticate():
                    # Retry the request
                    response = await method_func(f"api/{path.lstrip('/')}", **kwargs)
                else:
                    return None, 401, "Authentication failed"
            
            try:
                data = response.json() if response.content else None
            except json.JSONDecodeError:
                data = {"text": response.text}
            
            if response.status_code >= 400:
                error_msg = data.get("message", response.text) if data else response.text
                return data, response.status_code, error_msg
            
            return data, response.status_code, None
        
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None, 500, str(e)
