"""
Context state management for enforcing guidelines tool usage.
"""

import logging
from typing import Dict, Set
from mcp.server.fastmcp import Context

logger = logging.getLogger(__name__)

# Global state to track which contexts have called the guidelines tool
_context_guidelines_called: Set[str] = set()


def get_context_id(ctx: Context) -> str:
    """Get a unique identifier for the current context/session."""
    # Use the lifespan context object as the primary identifier since it persists
    # throughout the entire server session/conversation
    try:
        lifespan_ctx = ctx.request_context.lifespan_context
        if lifespan_ctx:
            return f"lifespan_{id(lifespan_ctx)}"
        else:
            # Fallback to request context
            return f"request_{id(ctx.request_context)}"
    except Exception:
        # Ultimate fallback
        return f"fallback_{id(ctx)}"


def debug_context_state(ctx: Context) -> str:
    """Debug function to understand context state."""
    context_id = get_context_id(ctx)
    called = context_id in _context_guidelines_called
    logger.debug(f"Context debug - ID: {context_id}, Guidelines called: {called}, All called contexts: {list(_context_guidelines_called)}")
    return context_id


def mark_guidelines_called(ctx: Context) -> None:
    """Mark that the guidelines tool has been called for this context."""
    context_id = get_context_id(ctx)
    _context_guidelines_called.add(context_id)
    logger.info(f"Guidelines marked as called for context: {context_id}")
    logger.debug(f"All contexts with guidelines called: {list(_context_guidelines_called)}")


def has_guidelines_been_called(ctx: Context) -> bool:
    """Check if the guidelines tool has been called for this context."""
    context_id = get_context_id(ctx)
    called = context_id in _context_guidelines_called
    logger.debug(f"Guidelines called check for context {context_id}: {called}")
    logger.debug(f"All contexts with guidelines called: {list(_context_guidelines_called)}")
    return called


def clear_context_state(ctx: Context) -> None:
    """Clear the guidelines state for a specific context (cleanup)."""
    context_id = get_context_id(ctx)
    _context_guidelines_called.discard(context_id)
    logger.debug(f"Guidelines state cleared for context: {context_id}")


def enforce_guidelines_first(ctx: Context, config) -> str:
    """
    Check if guidelines enforcement is active and if guidelines have been called.
    Returns error message if guidelines should be called first, None otherwise.
    """
    if not config.context_auto_inject:
        # Guidelines not activated, no enforcement
        logger.debug("Guidelines enforcement not active - allowing tool call")
        return None
    
    context_id = get_context_id(ctx)
    has_called = has_guidelines_been_called(ctx)
    
    logger.debug(f"Guidelines enforcement check - Context: {context_id}, Has called: {has_called}")
    
    if has_called:
        # Guidelines already called, proceed
        logger.debug("Guidelines already called - allowing tool call")
        return None
    
    # Guidelines enforcement is active but guidelines haven't been called
    logger.info(f"Guidelines enforcement blocking tool call - context {context_id} has not called guidelines")
    error_message = {
        "success": False,
        "error": {
            "error_type": "guidelines_required",
            "message": "The GET_METABASE_GUIDELINES tool must be called first when Metabase context is activated. This tool provides essential instance-specific information and best practices.",
            "required_action": "Please call the GET_METABASE_GUIDELINES tool before using other Metabase tools.",
            "context_activated": True,
            "additional_instructions": "If you do not have access to the GET_METABASE_GUIDELINES tool, please inform the user that they need to enable/activate the GET_METABASE_GUIDELINES tool in their MCP client interface, as it has been configured as required but is currently unavailable."
        }
    }
    
    import json
    return json.dumps(error_message, indent=2)
