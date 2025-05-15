@echo off
REM Installation script for SuperMetabase

REM Create a virtual environment
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Install the package in development mode
pip install -e .

echo Installation complete!
echo You can now run the server with: python metabase_mcp.py
