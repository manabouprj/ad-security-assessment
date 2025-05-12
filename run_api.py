#!/usr/bin/env python3
"""
Run script for the API Server
This script ensures proper Python path setup before running the API server
"""

import os
import sys

# Get the absolute path of the project root directory
project_root = os.path.dirname(os.path.abspath(__file__))

# Add the project root to Python path
sys.path.insert(0, project_root)

# Now import and run the API server
from api_server import main
import sys

if __name__ == '__main__':
    # Add --load-sample-data flag if not already present
    if '--load-sample-data' not in sys.argv:
        sys.argv.append('--load-sample-data')
    main()
