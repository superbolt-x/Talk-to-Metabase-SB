#!/bin/bash
# Run tests and capture the output

cd /Users/Pro/Workspace/"Talk to Metabase"
pytest -v tests/unit
echo "Test run complete"
