#!/bin/bash

echo "Active Directory Security Assessment Web UI"
echo "=========================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in the PATH."
    echo "Please install Python 3.8 or higher and try again."
    read -p "Press Enter to continue..."
    exit 1
fi

# Check if Node.js and npm are installed
echo "Checking for Node.js and npm..."
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in the PATH."
    echo "Please install Node.js and npm using your package manager:"
    echo "  - For Ubuntu/Debian: sudo apt install nodejs npm"
    echo "  - For CentOS/RHEL: sudo yum install nodejs npm"
    echo "  - For macOS with Homebrew: brew install node"
    echo "  - Or download from https://nodejs.org/"
    read -p "Press Enter to continue..."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed or not in the PATH."
    echo "npm usually comes with Node.js. Please install Node.js and npm using your package manager:"
    echo "  - For Ubuntu/Debian: sudo apt install nodejs npm"
    echo "  - For CentOS/RHEL: sudo yum install nodejs npm"
    echo "  - For macOS with Homebrew: brew install node"
    echo "  - Or download from https://nodejs.org/"
    read -p "Press Enter to continue..."
    exit 1
fi

# Print Node.js and npm versions
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

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
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    echo "Trying alternative activation method..."
    export VIRTUAL_ENV="$(pwd)/venv"
    export PATH="$VIRTUAL_ENV/bin:$PATH"
fi

# Verify virtual environment is activated
echo "Verifying virtual environment..."
./venv/bin/python -c "import sys; print('Python version:', sys.version); print('Virtual env:', sys.prefix)"
if [ $? -ne 0 ]; then
    echo "Error: Virtual environment verification failed."
    read -p "Press Enter to continue..."
    exit 1
fi

# Install setuptools first to ensure pkg_resources is available
echo "Installing setuptools..."
./venv/bin/pip install setuptools
if [ $? -ne 0 ]; then
    echo "Error: Failed to install setuptools."
    read -p "Press Enter to continue..."
    exit 1
fi

# Install required dependencies
echo "Installing required dependencies..."
./venv/bin/pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install required dependencies."
    read -p "Press Enter to continue..."
    exit 1
fi

# Ensure react-bootstrap-icons is installed
echo "Ensuring react-bootstrap-icons is installed..."
cd frontend
npm install react-bootstrap-icons --save --force --no-audit --no-fund --loglevel=error
if [ $? -ne 0 ]; then
    echo "Warning: Failed to install react-bootstrap-icons. Continuing anyway..."
fi
cd ..

# Run the web UI with sample data and debug mode for more verbose output
echo "Starting the Web UI with sample data..."
./venv/bin/python run_web_ui.py --load-sample-data --debug --no-browser

# Keep the virtual environment active until the script completes
echo
echo "Finished."
read -p "Press Enter to continue..."
