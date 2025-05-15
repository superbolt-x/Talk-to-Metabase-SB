#!/bin/bash
# Installation script for SuperMetabase

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the package in development mode
pip install -e .

# Make the entry point executable
chmod +x metabase_mcp.py

echo "Installation complete!"
echo "You can now run the server with: ./metabase_mcp.py"
echo "Or: python metabase_mcp.py"
