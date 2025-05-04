#!/usr/bin/env python3
"""
Setup script to ensure proper Python package structure
"""

import os
import sys

def create_init_files():
    """Create __init__.py files in all subdirectories of src"""
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
    
    # List of required package directories
    packages = ['core', 'config', 'reports', 'utils', 'tests']
    
    # Create src/__init__.py if it doesn't exist
    src_init = os.path.join(src_dir, '__init__.py')
    if not os.path.exists(src_init):
        with open(src_init, 'w') as f:
            f.write('"""Active Directory Security Assessment Tool package."""\n')
    
    # Create __init__.py in each package directory
    for package in packages:
        package_dir = os.path.join(src_dir, package)
        if not os.path.exists(package_dir):
            os.makedirs(package_dir)
        
        init_file = os.path.join(package_dir, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write(f'"""Active Directory Security Assessment Tool {package} package."""\n')

if __name__ == '__main__':
    create_init_files()
    print("Package structure setup complete.") 