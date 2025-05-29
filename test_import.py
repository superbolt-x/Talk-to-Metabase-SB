"""
Simple test for checking that the Talk to Metabase package can be imported.
"""

import sys

try:
    import talk_to_metabase
    from talk_to_metabase.config import MetabaseConfig
    from talk_to_metabase.server import create_server
    from talk_to_metabase.auth import MetabaseAuth
    
    print("All imports successful!")
    print(f"Talk to Metabase version: {talk_to_metabase.__version__}")
    print("Package structure seems correct.")
    sys.exit(0)
except ImportError as e:
    print(f"Import error: {e}")
    print("There might be issues with the package structure.")
    sys.exit(1)
