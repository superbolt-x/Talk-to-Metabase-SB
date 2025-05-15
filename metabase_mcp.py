#!/usr/bin/env python3
"""
SuperMetabase MCP Server entry point.
"""

import os
import sys
import logging
import traceback
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),  # Log to stderr for Claude Desktop to capture
    ],
)

logger = logging.getLogger("metabase_mcp")

# Load environment variables
try:
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except Exception as e:
    logger.warning(f"Failed to load .env file: {e}")

# Add the parent directory to the path if running as a script
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    logger.info(f"Added parent directory to path: {os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) }")

try:
    from supermetabase.server import run_server
    logger.info("Successfully imported supermetabase.server module")
    
    if __name__ == "__main__":
        logger.info("Starting SuperMetabase MCP server...")
        run_server()
except Exception as e:
    logger.error(f"Error starting server: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)
