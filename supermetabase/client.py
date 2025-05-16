"""
Metabase API client.
"""

import json
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
        self,
        query: Optional[str] = None,
        models: Optional[List[str]] = None,
        archived: bool = False,
        table_db_id: Optional[int] = None,
        filter_items_in_personal_collection: Optional[str] = None,
        created_at: Optional[str] = None,
        created_by: Optional[List[int]] = None,
        last_edited_at: Optional[str] = None,
        last_edited_by: Optional[List[int]] = None,
        search_native_query: Optional[bool] = None,
        verified: Optional[bool] = None,
        ids: Optional[List[int]] = None,
        include_dashboard_questions: bool = False,
        calculate_available_models: bool = False,
        context: Optional[str] = None,
        model_ancestors: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        Search for resources across Metabase with pagination.
        
        Args:
            query: Search term
            models: Types of resources to search for (card, dashboard, table, etc.)
            archived: Whether to include archived resources (default: False)
            table_db_id: Search for tables, cards, and models of a specific database ID
            filter_items_in_personal_collection: Filter items in personal collections 
                (options: all, only, only-mine, exclude, exclude-others)
            created_at: Search for items created at a specific timestamp
            created_by: Search for items created by specific user IDs
            last_edited_at: Search for items last edited at a specific timestamp
            last_edited_by: Search for items last edited by specific user IDs
            search_native_query: Whether to search the content of native queries
            verified: Whether to search for verified items only
            ids: Search for specific item IDs (works only with single value in models)
            include_dashboard_questions: Include questions from dashboards in results
            calculate_available_models: Calculate which models are available given filters
            context: Search context
            model_ancestors: Include model ancestors
            page: Page number for pagination (default: 1)
            page_size: Number of results per page (default: 20)
            
        Returns:
            Dict containing paginated search results and pagination metadata
        """
        # Start with optional query parameter
        params = {}
        if query:
            params["q"] = query
            
        # Add all other parameters
        if models:
            params["models"] = models
            logger.info(f"Search models parameter: {models}, type: {type(models)}")
        
        if archived:
            params["archived"] = "true"
            
        if table_db_id:
            params["table_db_id"] = str(table_db_id)
            
        if filter_items_in_personal_collection:
            params["filter_items_in_personal_collection"] = filter_items_in_personal_collection
            
        if created_at:
            params["created_at"] = created_at
            
        if created_by:
            params["created_by"] = created_by
            
        if last_edited_at:
            params["last_edited_at"] = last_edited_at
            
        if last_edited_by:
            params["last_edited_by"] = last_edited_by
            
        if search_native_query is not None:
            params["search_native_query"] = str(search_native_query).lower()
            
        if verified is not None:
            params["verified"] = str(verified).lower()
            
        if ids:
            params["ids"] = ids
            
        if include_dashboard_questions:
            params["include_dashboard_questions"] = "true"
            
        if calculate_available_models:
            params["calculate_available_models"] = "true"
            
        if context:
            params["context"] = context
            
        if model_ancestors:
            params["model_ancestors"] = "true"
        
        data, status, error = await self.auth.make_request(
            "GET", "search", params=params
        )
        
        if error:
            raise ValueError(f"Search failed: {error}")
        
        # Get all results first
        all_results = []
        if isinstance(data, dict) and 'data' in data:
            all_results = data['data'] if isinstance(data['data'], list) else []
        elif isinstance(data, list):
            all_results = data
        
        # Calculate pagination metadata
        total_count = len(all_results)
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_count)
        
        # Slice the results for the requested page
        paginated_results = all_results[start_idx:end_idx] if start_idx < total_count else []
        
        # Return results with pagination metadata
        return {
            "results": paginated_results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_more": page < total_pages
            }
        }

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
