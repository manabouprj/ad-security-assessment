#!/usr/bin/env python3
"""
Dependency Checker for Active Directory Security Assessment Agent

This script checks if all required dependencies are installed and offers to install
any missing packages before running the main application.
"""

import sys
import subprocess
import importlib.util
import os
from typing import List, Tuple, Dict

# Try to import pkg_resources, but provide a fallback if it's not available
try:
    import pkg_resources
    HAS_PKG_RESOURCES = True
except ImportError:
    HAS_PKG_RESOURCES = False
    print("Warning: pkg_resources not found. Installing setuptools...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'setuptools'])
        import pkg_resources
        HAS_PKG_RESOURCES = True
    except Exception as e:
        print(f"Error installing setuptools: {str(e)}")
        print("Will use importlib for basic dependency checking instead.")

def get_required_packages() -> List[str]:
    """
    Get the list of required packages from requirements.txt.
    
    Returns:
        List of required package names with versions
    """
    required_packages = []
    
    # Import platform module for condition evaluation
    import platform
    
    # Create evaluation context with necessary variables
    eval_context = {
        'sys_platform': sys.platform,
        'platform_system': platform.system(),
        'platform_machine': platform.machine(),
        'platform_python_implementation': platform.python_implementation()
    }
    
    try:
        with open('requirements.txt', 'r') as f:
            for line in f:
                # Skip comments and empty lines
                line = line.strip()
                if line and not line.startswith('#'):
                    # Handle platform-specific dependencies
                    if ';' in line:
                        pkg, condition = line.split(';', 1)
                        try:
                            # Only include if the condition is met
                            if eval(condition.strip(), {"__builtins__": {}}, eval_context):
                                required_packages.append(pkg.strip())
                        except Exception as e:
                            print(f"Warning: Could not evaluate condition '{condition.strip()}': {str(e)}")
                            print(f"Including package '{pkg.strip()}' anyway.")
                            required_packages.append(pkg.strip())
                    else:
                        required_packages.append(line)
    except FileNotFoundError:
        print("Error: requirements.txt file not found.")
        sys.exit(1)
    
    return required_packages

def check_package(package_spec: str) -> Tuple[bool, str, str]:
    """
    Check if a package is installed and get its version.
    
    Args:
        package_spec: Package specification (e.g., 'package>=1.0.0')
        
    Returns:
        Tuple of (is_installed, package_name, required_version)
    """
    # Parse package name and version
    if '>=' in package_spec:
        package_name, required_version = package_spec.split('>=', 1)
    elif '==' in package_spec:
        package_name, required_version = package_spec.split('==', 1)
    elif '<=' in package_spec:
        package_name, required_version = package_spec.split('<=', 1)
    else:
        package_name = package_spec
        required_version = None
    
    package_name = package_name.strip()
    
    # Use pkg_resources if available
    if HAS_PKG_RESOURCES:
        try:
            # Check if package is installed
            installed_version = pkg_resources.get_distribution(package_name).version
            return True, package_name, installed_version
        except pkg_resources.DistributionNotFound:
            return False, package_name, required_version
    else:
        # Fallback to importlib if pkg_resources is not available
        try:
            # Try to import the package
            spec = importlib.util.find_spec(package_name)
            if spec is not None:
                # Package is installed, but we don't know the version
                return True, package_name, "Unknown"
            else:
                return False, package_name, required_version
        except (ImportError, AttributeError):
            # If there's an error, assume the package is not installed
            return False, package_name, required_version

def check_dependencies() -> Dict[str, List[str]]:
    """
    Check all dependencies and return lists of installed and missing packages.
    
    Returns:
        Dictionary with 'installed' and 'missing' package lists
    """
    required_packages = get_required_packages()
    installed_packages = []
    missing_packages = []
    
    print("Checking dependencies...")
    
    for package_spec in required_packages:
        is_installed, package_name, version = check_package(package_spec)
        
        if is_installed:
            installed_packages.append(f"{package_name} ({version})")
        else:
            missing_packages.append(package_spec)
    
    return {
        'installed': installed_packages,
        'missing': missing_packages
    }

def install_packages(packages: List[str]) -> bool:
    """
    Install missing packages using pip.
    
    Args:
        packages: List of packages to install
        
    Returns:
        True if installation was successful, False otherwise
    """
    if not packages:
        return True
    
    print(f"Installing {len(packages)} missing packages...")
    
    try:
        # Use subprocess to run pip
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main entry point for the dependency checker."""
    print("Active Directory Security Assessment Agent - Dependency Checker")
    print("=" * 60)
    
    # Check dependencies
    result = check_dependencies()
    
    # Display results
    if result['installed']:
        print(f"\n{len(result['installed'])} required packages are already installed:")
        for package in result['installed']:
            print(f"  ✓ {package}")
    
    # Handle missing packages
    if result['missing']:
        print(f"\n{len(result['missing'])} required packages are missing:")
        for package in result['missing']:
            print(f"  ✗ {package}")
        
        # Ask to install missing packages
        install_choice = input("\nDo you want to install the missing packages? (y/n): ").strip().lower()
        
        if install_choice == 'y':
            if install_packages(result['missing']):
                print("\nAll missing packages have been successfully installed.")
            else:
                print("\nFailed to install some packages. Please install them manually:")
                print("  pip install " + " ".join(result['missing']))
                return 1
        else:
            print("\nPlease install the missing packages manually before running the application:")
            print("  pip install " + " ".join(result['missing']))
            return 1
    else:
        print("\nAll required dependencies are installed.")
    
    # Check if we're being run from one of our scripts
    run_from_script = os.environ.get('RUN_FROM_SCRIPT') == '1'
    
    if not run_from_script:
        # Ask to run the main application
        run_choice = input("\nDo you want to run the Active Directory Security Assessment Agent now? (y/n): ").strip().lower()
        
        if run_choice == 'y':
            print("\nStarting Active Directory Security Assessment Agent...\n")
            try:
                # Use subprocess to run the main script
                subprocess.call([sys.executable, 'main.py'])
            except Exception as e:
                print(f"Error running the application: {str(e)}")
                return 1
    else:
        # If run from script, just continue
        print("\nDependency check complete. Continuing with the script...\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
