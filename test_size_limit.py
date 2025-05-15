#!/usr/bin/env python3
"""
Test script to verify response size limit functionality.
"""

import json
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("test_size_limit")

# Load environment variables
load_dotenv()

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from supermetabase.config import MetabaseConfig
from supermetabase.tools.common import check_response_size

def test_size_limit():
    """Test the size limit functionality."""
    # Get the response size limit from environment
    try:
        response_size_limit = int(os.environ.get("RESPONSE_SIZE_LIMIT", "100000"))
    except ValueError:
        response_size_limit = 100000
    
    logger.info(f"Testing with response size limit: {response_size_limit}")
    
    # Create a test config
    config = MetabaseConfig(
        url="https://test.example.com/",
        username="test",
        password="test",
        response_size_limit=response_size_limit
    )
    
    # Test 1: Response under the limit
    short_response = "This is a short response."
    result_1 = check_response_size(short_response, config)
    
    if result_1 == short_response:
        logger.info("✅ Test 1 passed: Short response returned as-is")
    else:
        logger.error("❌ Test 1 failed: Short response was modified unexpectedly")
    
    # Test 2: Response over the limit
    # Generate a large response by repeating characters
    long_response = "X" * (response_size_limit + 1000)
    result_2 = check_response_size(long_response, config)
    
    try:
        # Parse the result as JSON
        error_data = json.loads(result_2)
        
        if not error_data.get("success", True):
            logger.info("✅ Test 2 passed: Large response was properly limited")
            logger.info(f"Error message: {error_data.get('error', {}).get('message', '')}")
        else:
            logger.error("❌ Test 2 failed: Large response didn't trigger error")
    except json.JSONDecodeError:
        logger.error("❌ Test 2 failed: Response is not valid JSON")
    
    # Test 3: Response exactly at the limit
    exact_response = "X" * response_size_limit
    result_3 = check_response_size(exact_response, config)
    
    if result_3 == exact_response:
        logger.info("✅ Test 3 passed: Response at exact limit returned as-is")
    else:
        logger.error("❌ Test 3 failed: Response at exact limit was modified unexpectedly")

if __name__ == "__main__":
    test_size_limit()
