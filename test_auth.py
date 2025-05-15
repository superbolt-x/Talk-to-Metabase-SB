#!/usr/bin/env python3
"""
Test script to check Metabase authentication.
"""

import asyncio
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

# Add the parent directory to the path if running as a script
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables
load_dotenv()

from supermetabase.config import MetabaseConfig
from supermetabase.auth import MetabaseAuth


async def test_authentication():
    """Test authentication with Metabase."""
    # Get config from environment variables
    try:
        config = MetabaseConfig.from_env()
        print(f"Config loaded from environment variables:")
        print(f"  URL: {config.url}")
        print(f"  Username: {config.username}")
        print(f"  Password: {'*' * len(config.password)}")
    except Exception as e:
        print(f"Error loading config: {e}")
        return False
    
    # Create auth client
    auth = MetabaseAuth(config)
    
    try:
        # Test authentication
        print("\nTesting authentication...")
        result = await auth.authenticate()
        
        if result:
            print(f"✅ Authentication successful!")
            print(f"Session token: {auth.session_token[:10]}..." if auth.session_token else "No token")
            
            # Test a simple API call
            print("\nTesting API call to get current user...")
            data, status, error = await auth.make_request("GET", "user/current")
            
            if error:
                print(f"❌ API call failed: {error} (status: {status})")
                return False
            else:
                print(f"✅ API call successful (status: {status})")
                print(f"Current user: {data.get('first_name', '')} {data.get('last_name', '')} ({data.get('email', '')})")
                return True
        else:
            print("❌ Authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return False
    finally:
        # Clean up
        await auth.close()


if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_authentication())
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed")
        sys.exit(1)
