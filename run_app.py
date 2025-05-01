#!/usr/bin/env python3
"""
Direct runner for Active Directory Security Assessment Agent

This script directly runs the main application after ensuring all dependencies are installed.
"""

import sys
import subprocess
import os

def main():
    """Main entry point for the application runner."""
    print("Active Directory Security Assessment Agent - Direct Runner")
    print("=" * 60)
    
    # Check if we're in a virtual environment
    in_venv = sys.prefix != sys.base_prefix
    
    if not in_venv:
        print("\nWarning: You are not running in a virtual environment.")
        print("It is recommended to use run.sh or run.bat instead.")
        choice = input("Do you want to continue anyway? (y/n): ").strip().lower()
        if choice != 'y':
            print("Exiting. Please use run.sh or run.bat to set up a proper environment.")
            return 1
    
    # Install setuptools first to ensure pkg_resources is available
    print("\nInstalling setuptools...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'setuptools'])
    except subprocess.CalledProcessError:
        print("Warning: Failed to install setuptools.")
    
    # Install dependencies if needed
    print("\nEnsuring all dependencies are installed...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies.")
        return 1
    
    # Run the main application in mock mode by default
    print("\nStarting Active Directory Security Assessment Agent in mock mode...\n")
    try:
        # Use subprocess to run the main script with mock mode enabled
        subprocess.call([sys.executable, 'main.py', '--mock'])
    except Exception as e:
        print(f"Error running the application: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
