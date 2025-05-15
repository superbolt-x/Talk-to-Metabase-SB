"""
Error handling utilities.
"""

from typing import Any, Dict, List, Optional, TypeVar, Union


class MetabaseError(Exception):
    """Base error class for Metabase API errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        endpoint: Optional[str] = None,
        metabase_error: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.endpoint = endpoint
        self.metabase_error = metabase_error
        
        error_msg = f"Metabase API Error: {message}"
        if status_code:
            error_msg += f" (Status: {status_code})"
        if endpoint:
            error_msg += f" (Endpoint: {endpoint})"
            
        super().__init__(error_msg)


class AuthenticationError(MetabaseError):
    """Error during authentication with Metabase."""
    pass


class ResourceNotFoundError(MetabaseError):
    """Error when a resource is not found."""
    pass


class PermissionError(MetabaseError):
    """Error when permissions are insufficient."""
    pass


class ValidationError(MetabaseError):
    """Error when request validation fails."""
    pass


class ServerError(MetabaseError):
    """Error when the Metabase server experiences an internal error."""
    pass


def classify_error(
    status_code: int, 
    message: str, 
    endpoint: Optional[str] = None,
    metabase_error: Optional[Dict[str, Any]] = None
) -> MetabaseError:
    """
    Classify an error based on the status code and return the appropriate error type.
    
    Args:
        status_code: HTTP status code
        message: Error message
        endpoint: API endpoint that returned the error
        metabase_error: Original error from Metabase
        
    Returns:
        Classified error instance
    """
    if status_code == 401:
        return AuthenticationError(message, status_code, endpoint, metabase_error)
    elif status_code == 403:
        return PermissionError(message, status_code, endpoint, metabase_error)
    elif status_code == 404:
        return ResourceNotFoundError(message, status_code, endpoint, metabase_error)
    elif status_code == 400 or status_code == 422:
        return ValidationError(message, status_code, endpoint, metabase_error)
    elif status_code >= 500:
        return ServerError(message, status_code, endpoint, metabase_error)
    else:
        return MetabaseError(message, status_code, endpoint, metabase_error)
