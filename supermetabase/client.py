"""
Metabase API client.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from .auth import MetabaseAuth

logger = logging.getLogger(__name__)


class MetabaseClient:
    """Client for the Metabase API."""

    def __init__(self, auth: MetabaseAuth):
        """Initialize with authentication."""
        self.auth = auth

    async def get_resource(self, resource_type: str, resource_id: int) -> Dict[str, Any]:
        """
        Get a resource by type and ID.
        
        Args:
            resource_type: Type of resource (dashboard, card, collection, etc.)
            resource_id: ID of the resource
            
        Returns:
            Resource data
        """
        data, status, error = await self.auth.make_request(
            "GET", f"{resource_type}/{resource_id}"
        )
        
        if error:
            raise ValueError(f"Failed to get {resource_type}/{resource_id}: {error}")
        
        return data

    async def create_resource(
        self, resource_type: str, resource_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new resource.
        
        Args:
            resource_type: Type of resource (dashboard, card, collection, etc.)
            resource_data: Data for the new resource
            
        Returns:
            Created resource data
        """
        data, status, error = await self.auth.make_request(
            "POST", f"{resource_type}", json=resource_data
        )
        
        if error:
            raise ValueError(f"Failed to create {resource_type}: {error}")
        
        return data

    async def update_resource(
        self, resource_type: str, resource_id: int, resource_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing resource.
        
        Args:
            resource_type: Type of resource (dashboard, card, collection, etc.)
            resource_id: ID of the resource
            resource_data: Updated data for the resource
            
        Returns:
            Updated resource data
        """
        data, status, error = await self.auth.make_request(
            "PUT", f"{resource_type}/{resource_id}", json=resource_data
        )
        
        if error:
            raise ValueError(f"Failed to update {resource_type}/{resource_id}: {error}")
        
        return data

    async def delete_resource(
        self, resource_type: str, resource_id: int
    ) -> Dict[str, Any]:
        """
        Delete a resource.
        
        Args:
            resource_type: Type of resource (dashboard, card, collection, etc.)
            resource_id: ID of the resource
            
        Returns:
            Deletion response data
        """
        data, status, error = await self.auth.make_request(
            "DELETE", f"{resource_type}/{resource_id}"
        )
        
        if error:
            raise ValueError(f"Failed to delete {resource_type}/{resource_id}: {error}")
        
        return data

    async def search(
        self, query: str, models: Optional[List[str]] = None, archived: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for resources across Metabase.
        
        Args:
            query: Search term
            models: Types of resources to search for (card, dashboard, etc.)
            archived: Whether to include archived resources
            
        Returns:
            List of matching resources
        """
        params = {"q": query}
        
        if models:
            params["models"] = models
        
        if archived:
            params["archived"] = "true"
        
        data, status, error = await self.auth.make_request(
            "GET", "search", params=params
        )
        
        if error:
            raise ValueError(f"Search failed: {error}")
        
        return data if isinstance(data, list) else []

    async def execute_query(
        self, query_type: str, query_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a query against a database.
        
        Args:
            query_type: Type of query (native, query)
            query_data: Query parameters
            
        Returns:
            Query results
        """
        data, status, error = await self.auth.make_request(
            "POST", "dataset", json={"type": query_type, **query_data}
        )
        
        if error:
            raise ValueError(f"Query execution failed: {error}")
        
        return data
