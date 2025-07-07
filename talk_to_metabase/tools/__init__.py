"""
MCP tools for Metabase integration.
"""
import logging

logger = logging.getLogger(__name__)

# Import all tool modules to register their tools
try:
    from . import common
    logger.info("Loaded common tools module")
    
    # Import resources module to ensure it's available for PyInstaller
    from .. import resources
    logger.info("Loaded resources module")
    
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
    
    from . import dataset
    logger.info("Loaded dataset tools module")
    
    from . import visualization
    logger.info("Loaded visualization tools module")
    
    from . import dashcards
    logger.info("Loaded dashcards tools module")
    
    from . import parameters
    logger.info("Loaded parameters tools module")
    
    from . import card_parameters
    logger.info("Loaded card_parameters tools module")
    
    from . import mbql
    logger.info("Loaded mbql tools module")
    
    # Context tools will be loaded lazily when the server starts
    logger.info("Core tools modules loaded successfully")
except Exception as e:
    logger.error(f"Error loading tool modules: {e}")
