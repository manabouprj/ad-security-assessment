#!/usr/bin/env python3
"""
Test runner for the Active Directory Security Assessment Agent.
"""

import os
import sys
import unittest
import argparse
import logging

def run_tests(test_path=None, verbose=False):
    """
    Run the test suite.
    
    Args:
        test_path: Path to specific test file or directory (optional)
        verbose: Whether to show verbose output
    
    Returns:
        True if all tests pass, False otherwise
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Discover and run tests
    if test_path:
        if os.path.isfile(test_path):
            # Run specific test file
            test_suite = unittest.defaultTestLoader.discover(
                os.path.dirname(test_path),
                pattern=os.path.basename(test_path)
            )
        else:
            # Run all tests in directory
            test_suite = unittest.defaultTestLoader.discover(test_path)
    else:
        # Run all tests
        test_suite = unittest.defaultTestLoader.discover('src/tests')
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = test_runner.run(test_suite)
    
    # Return True if all tests pass
    return result.wasSuccessful()

def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description='Run tests for the Active Directory Security Assessment Agent')
    parser.add_argument('--test-path', type=str, help='Path to specific test file or directory')
    parser.add_argument('--verbose', action='store_true', help='Show verbose output')
    
    args = parser.parse_args()
    
    success = run_tests(args.test_path, args.verbose)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
