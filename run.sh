#!/bin/bash

echo "Active Directory Security Assessment Agent"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in the PATH."
    echo "Please install Python 3.8 or higher and try again."
    read -p "Press Enter to continue..."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        read -p "Press Enter to continue..."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install setuptools first to ensure pkg_resources is available
echo "Installing setuptools..."
pip install setuptools

# Install required dependencies
echo "Installing required dependencies..."
pip install -r requirements.txt

# Run dependency checker
echo "Running dependency checker..."
export RUN_FROM_SCRIPT=1
python check_dependencies.py

# Run the main application in mock mode by default
echo "Running the application in mock mode..."
python main.py --mock

# Keep the virtual environment active until the script completes
# The deactivate command will be called by the dependency checker if needed

echo
echo "Finished."
read -p "Press Enter to continue..."
