"""
Simple test for checking that the SuperMetabase package can be imported.
"""

import sys

try:
    import supermetabase
    from supermetabase.config import MetabaseConfig
    from supermetabase.server import create_server
    from supermetabase.auth import MetabaseAuth
    
    print("All imports successful!")
    print(f"SuperMetabase version: {supermetabase.__version__}")
    print("Package structure seems correct.")
    sys.exit(0)
except ImportError as e:
    print(f"Import error: {e}")
    print("There might be issues with the package structure.")
    sys.exit(1)
