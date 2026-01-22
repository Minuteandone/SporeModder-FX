#!/bin/bash
"""
DBPF Explorer Launcher Script

This script provides a convenient way to launch the DBPF Explorer
application from the command line.
"""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if required files exist
if [ ! -f "$SCRIPT_DIR/dbpf_explorer.py" ]; then
    echo "Error: dbpf_explorer.py not found in $SCRIPT_DIR"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/dbpf_interface.py" ]; then
    echo "Error: dbpf_interface.py not found in $SCRIPT_DIR"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/dbpf_unpacker.py" ]; then
    echo "Error: dbpf_unpacker.py not found in $SCRIPT_DIR"
    exit 1
fi

# Launch the application
echo "Starting DBPF Explorer..."
cd "$SCRIPT_DIR"
python3 dbpf_explorer.py

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "DBPF Explorer exited with code $EXIT_CODE"
fi

exit $EXIT_CODE</content>
<parameter name="filePath">/workspaces/SporeModder-FX/launch_dbpf_explorer.sh