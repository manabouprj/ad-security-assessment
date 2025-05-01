#!/usr/bin/env python3
"""
Active Directory Security Assessment Agent

This tool integrates with Active Directory to perform security assessments
based on Microsoft Security Configuration Toolkit standards.
"""

import argparse
import logging
import sys
import os
import getpass
from datetime import datetime

from src.core.ad_connector import ADConnector
from src.core.security_assessment import SecurityAssessment
from src.reports.report_generator import ReportGenerator
from src.config.config_manager import ConfigManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"ad_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Active Directory Security Assessment Tool')
    parser.add_argument('--config', type=str, default='config.json', 
                        help='Path to configuration file')
    parser.add_argument('--output-dir', type=str, default='reports',
                        help='Directory to store output reports')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--domain', type=str,
                        help='Domain to assess (overrides config file)')
    parser.add_argument('--server', type=str,
                        help='Domain controller to connect to (overrides config file)')
    parser.add_argument('--interactive', action='store_true',
                        help='Enable interactive mode to input domain information')
    parser.add_argument('--save-config', action='store_true',
                        help='Save provided information to config file')
    parser.add_argument('--mock', action='store_true',
                        help='Run in mock mode without connecting to an actual AD server')
    
    return parser.parse_args()

def interactive_config(config_manager, config):
    """
    Interactively collect configuration information from the user.
    
    Args:
        config_manager: ConfigManager instance
        config: Current configuration dictionary
        
    Returns:
        Updated configuration dictionary
    """
    print("\n=== Active Directory Security Assessment Configuration ===\n")
    
    # Domain information
    print("Domain Information:")
    domain = input(f"Domain name [{config.get('domain', '')}]: ").strip()
    if domain:
        config['domain'] = domain
    
    server = input(f"Domain controller hostname/IP [{config.get('server', '')}]: ").strip()
    if server:
        config['server'] = server
    
    # Authentication
    print("\nAuthentication (leave blank to use current credentials):")
    username = input(f"Username [{config.get('username', '')}]: ").strip()
    if username:
        config['username'] = username
    
    use_password = input("Do you want to enter a password? (y/n) [n]: ").strip().lower()
    if use_password == 'y':
        password = getpass.getpass("Password: ")
        if password:
            config['password'] = password
    
    # Connection settings
    print("\nConnection Settings:")
    use_ssl = input(f"Use SSL/TLS (LDAPS)? (y/n) [{('y' if config.get('use_ssl', True) else 'n')}]: ").strip().lower()
    if use_ssl in ('y', 'n'):
        config['use_ssl'] = (use_ssl == 'y')
    
    if config.get('use_ssl', True):
        verify_ssl = input(f"Verify SSL certificates? (y/n) [{('y' if config.get('verify_ssl', True) else 'n')}]: ").strip().lower()
        if verify_ssl in ('y', 'n'):
            config['verify_ssl'] = (verify_ssl == 'y')
    
    # Report settings
    print("\nReport Settings:")
    company_name = input(f"Company name for reports [{config.get('report', {}).get('company_name', 'Your Company')}]: ").strip()
    if company_name:
        if 'report' not in config:
            config['report'] = {}
        config['report']['company_name'] = company_name
    
    print("\nConfiguration complete!\n")
    
    return config

def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        
        # Interactive mode
        if args.interactive:
            logger.info("Starting interactive configuration...")
            config = interactive_config(config_manager, config)
            
            # Save configuration if requested
            if args.save_config:
                logger.info("Saving configuration...")
                config_manager.update_config(config)
        
        # Override config with command line arguments if provided
        if args.domain:
            config['domain'] = args.domain
        if args.server:
            config['server'] = args.server
        if args.mock:
            config['mock_mode'] = True
        
        # Validate required configuration
        if not config.get('domain') and not args.mock and not config.get('mock_mode'):
            logger.error("Domain name is required unless running in mock mode. Please provide it using --domain, --interactive, or in the config file.")
            return 1
            
        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Connect to Active Directory
        if args.mock or config.get('mock_mode'):
            logger.info("Running in mock mode with simulated AD data")
            if not config.get('domain'):
                config['domain'] = 'example.com'  # Set a default domain for mock mode
        else:
            logger.info(f"Connecting to Active Directory domain: {config['domain']}...")
            
        ad_connector = ADConnector(config)
        
        # Perform security assessment
        logger.info("Starting security assessment...")
        assessment = SecurityAssessment(ad_connector, config)
        assessment_results = assessment.run_assessment()
        
        # Generate reports
        logger.info("Generating reports...")
        report_generator = ReportGenerator(assessment_results, args.output_dir)
        csv_path = report_generator.generate_csv_report()
        executive_path, technical_path = report_generator.generate_pdf_report()
        
        logger.info(f"Assessment complete. Reports saved to:")
        logger.info(f"  CSV: {csv_path}")
        logger.info(f"  Executive Dashboard: {executive_path}")
        logger.info(f"  Technical Report: {technical_path}")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
