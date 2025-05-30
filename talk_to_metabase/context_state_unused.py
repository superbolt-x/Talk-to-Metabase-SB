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
    # Use the lifespan context which should persist across tool calls
    try:
        lifespan_ctx = ctx.request_context.lifespan_context
        return str(id(lifespan_ctx))
    except AttributeError:
        # Fallback to request context if lifespan context doesn't exist
        return str(id(ctx.request_context))


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
    logger.info(f"[CONTEXT] Guidelines marked as called for context: {context_id}")
    logger.info(f"[CONTEXT] All called contexts: {list(_context_guidelines_called)}")


def has_guidelines_been_called(ctx: Context) -> bool:
    """Check if the guidelines tool has been called for this context."""
    context_id = get_context_id(ctx)
    called = context_id in _context_guidelines_called
    logger.info(f"[CONTEXT] Checking guidelines for context {context_id}: {called}")
    logger.info(f"[CONTEXT] All called contexts: {list(_context_guidelines_called)}")
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
        return None
    
    if has_guidelines_been_called(ctx):
        # Guidelines already called, proceed
        return None
    
    # Guidelines enforcement is active but guidelines haven't been called
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
