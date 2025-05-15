"""
MCP tools for Metabase integration.
"""
import logging

logger = logging.getLogger(__name__)

# Import all tool modules to register their tools
try:
    from . import common
    logger.info("Loaded common tools module")
    
    from . import dashboard
    logger.info("Loaded dashboard tools module")
    
    from . import card
    logger.info("Loaded card tools module")
    
    from . import collection
    logger.info("Loaded collection tools module")
    
    from . import database
    logger.info("Loaded database tools module")
    
    from . import search
    logger.info("Loaded search tools module")
except Exception as e:
    logger.error(f"Error loading tool modules: {e}")
