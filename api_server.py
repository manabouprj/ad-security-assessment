#!/usr/bin/env python3
"""
API Server for Active Directory Security Assessment Agent

This module provides a REST API for the React frontend to interact with the
Active Directory Security Assessment Agent.
"""

import os
import json
import logging
import argparse
import subprocess
import sys
from datetime import datetime
from flask import Flask, jsonify, request, send_file, Response, session
from flask_cors import CORS
import src.core.security_assessment as security_assessment
from src.core.ad_connector import ADConnector
from src.config.config_manager import ConfigManager
from src.reports.report_generator import ReportGenerator
from functools import wraps
import hashlib
import re
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key
CORS(app, supports_credentials=True)  # Enable CORS with credentials

# Global variables
config_manager = ConfigManager('config.json')
assessment_results = None
last_assessment_time = None

# Add authentication configuration
AUTH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auth_config.json')
DEFAULT_USERNAME = 'Orunmila'

def load_auth_config():
    """Load authentication configuration from file"""
    try:
        if os.path.exists(AUTH_FILE):
            with open(AUTH_FILE, 'r') as f:
                config = json.load(f)
                # If the file is empty or doesn't have required fields
                if not config or not isinstance(config, dict):
                    config = {
                        'username': DEFAULT_USERNAME,
                        'password_hash': None,
                        'password_changed': False
                    }
                # Ensure the config has all required fields
                if 'password_hash' not in config:
                    config['password_hash'] = None
                if 'password_changed' not in config:
                    config['password_changed'] = False
                if 'username' not in config:
                    config['username'] = DEFAULT_USERNAME
                return config
        else:
            # Create new auth config without a password
            config = {
                'username': DEFAULT_USERNAME,
                'password_hash': None,
                'password_changed': False
            }
            # Ensure the directory exists
            os.makedirs(os.path.dirname(AUTH_FILE), exist_ok=True)
            save_auth_config(config)
            return config
    except Exception as e:
        print(f"Error loading auth config: {e}")
        return None

def save_auth_config(config):
    """Save authentication configuration to file"""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(AUTH_FILE), exist_ok=True)
        with open(AUTH_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Auth config saved to {AUTH_FILE}")  # Debug log
    except Exception as e:
        print(f"Error saving auth config: {e}")

def validate_password(password):
    """Validate password meets requirements"""
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    if len(re.findall(r'[A-Z]', password)) < 2:
        return False, "Password must contain at least 2 uppercase letters"
    if len(re.findall(r'[a-z]', password)) < 3:
        return False, "Password must contain at least 3 lowercase letters"
    if len(re.findall(r'[0-9]', password)) < 2:
        return False, "Password must contain at least 2 numbers"
    if len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', password)) < 1:
        return False, "Password must contain at least 1 special character"
    return True, None

def login_required(f):
    """Decorator to require login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        auth_config = load_auth_config()
        if not auth_config:
            return jsonify({'error': 'Authentication configuration error'}), 500

        if username != auth_config['username']:
            return jsonify({'error': 'Invalid username'}), 401

        # If this is the first login (no password set)
        if auth_config['password_hash'] is None:
            # Validate the new password
            is_valid, error_message = validate_password(password)
            if not is_valid:
                return jsonify({'error': error_message}), 400

            # Hash and save the new password
            auth_config['password_hash'] = generate_password_hash(password)
            auth_config['password_changed'] = True
            save_auth_config(auth_config)
            
            # Set session variables
            session['authenticated'] = True
            session['username'] = username
            session['password_changed'] = True
            
            return jsonify({
                'message': 'Password created successfully',
                'password_changed': True
            }), 200

        # Normal login with existing password
        if check_password_hash(auth_config['password_hash'], password):
            session['authenticated'] = True
            session['username'] = username
            session['password_changed'] = auth_config['password_changed']
            return jsonify({
                'message': 'Login successful',
                'password_changed': auth_config['password_changed']
            }), 200
        else:
            print(f"Password mismatch. Stored hash: {auth_config['password_hash']}")
            return jsonify({'error': 'Invalid password'}), 401

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    try:
        session.clear()
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/api/auth/change-password', methods=['POST'])
@login_required
def change_password():
    """Handle password change."""
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new passwords are required'}), 400
    
    auth_config = load_auth_config()
    
    if check_password_hash(auth_config['password_hash'], current_password):
        # Validate new password
        is_valid, error_message = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Update password
        auth_config['password_hash'] = generate_password_hash(new_password)
        auth_config['password_changed'] = True
        save_auth_config(auth_config)
        
        # Update session
        session['password_changed'] = True
        
        return jsonify({'message': 'Password changed successfully'})
    else:
        return jsonify({'error': 'Current password is incorrect'}), 401

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    try:
        auth_config = load_auth_config()
        if not auth_config:
            return jsonify({
                'authenticated': False,
                'username': None,
                'password_changed': False
            })

        return jsonify({
            'authenticated': session.get('authenticated', False),
            'username': session.get('username'),
            'password_changed': session.get('password_changed', False)
        })
    except Exception as e:
        print(f"Auth status error: {e}")
        return jsonify({
            'authenticated': False,
            'username': None,
            'password_changed': False
        }), 500

@app.route('/api/assessment/results', methods=['GET'])
@login_required
def get_assessment_results():
    """Get the latest assessment results."""
    global assessment_results, last_assessment_time
    
    if assessment_results is None:
        return jsonify({
            'error': 'No assessment results available',
            'message': 'Run an assessment first'
        }), 404
    
    # Add timestamp to results
    results_with_timestamp = {
        **assessment_results,
        'timestamp': last_assessment_time.isoformat() if last_assessment_time else None
    }
    
    return jsonify(results_with_timestamp)

@app.route('/api/assessment/run', methods=['POST'])
@login_required
def run_assessment():
    """Run a new security assessment with the provided configuration."""
    global assessment_results, last_assessment_time
    
    try:
        # Get configuration from request
        config_data = request.json
        
        # Update configuration
        if config_data:
            config_manager.update_config(config_data)
        
        # Get the current configuration
        config = config_manager.get_config()
        
        # Initialize AD connector
        ad_connector = ADConnector(config)
        
        # Run assessment
        logger.info("Starting security assessment")
        assessment = security_assessment.SecurityAssessment(ad_connector)
        assessment_results = assessment.run_assessment()
        last_assessment_time = datetime.now()
        
        # Save results to file
        results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        results_file = os.path.join(
            results_dir, 
            f"assessment_{last_assessment_time.strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(results_file, 'w') as f:
            json.dump(assessment_results, f, indent=2)
        
        logger.info(f"Assessment completed and saved to {results_file}")
        
        return jsonify({
            'success': True,
            'message': 'Assessment completed successfully',
            'timestamp': last_assessment_time.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error running assessment: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to run assessment',
            'message': str(e)
        }), 500

@app.route('/api/domain-controllers', methods=['GET'])
def get_domain_controllers():
    """Get domain controller information."""
    global assessment_results
    
    if assessment_results is None or 'domain_controllers' not in assessment_results:
        return jsonify({
            'error': 'No domain controller data available',
            'message': 'Run an assessment first'
        }), 404
    
    return jsonify(assessment_results['domain_controllers'])

@app.route('/api/computers', methods=['GET'])
def get_computers():
    """Get computer information."""
    global assessment_results
    
    if assessment_results is None or 'computers' not in assessment_results:
        return jsonify({
            'error': 'No computer data available',
            'message': 'Run an assessment first'
        }), 404
    
    return jsonify(assessment_results['computers'])

@app.route('/api/domain-policies', methods=['GET'])
def get_domain_policies():
    """Get domain policy information."""
    global assessment_results
    
    if assessment_results is None or 'domain_policies' not in assessment_results:
        return jsonify({
            'error': 'No domain policy data available',
            'message': 'Run an assessment first'
        }), 404
    
    return jsonify(assessment_results['domain_policies'])

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get the current configuration."""
    config = config_manager.get_config()
    
    # Don't return password in the response
    if 'password' in config:
        config = {**config}  # Create a copy
        del config['password']
    
    return jsonify(config)

@app.route('/api/config', methods=['PUT'])
def update_config():
    """Update the configuration."""
    try:
        config_data = request.json
        config_manager.update_config(config_data)
        
        # Don't return password in the response
        config = config_manager.get_config()
        if 'password' in config:
            config = {**config}  # Create a copy
            del config['password']
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully',
            'config': config
        })
        
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to update configuration',
            'message': str(e)
        }), 500

@app.route('/api/reports/<report_type>', methods=['GET'])
def get_report(report_type):
    """Generate and download a report."""
    global assessment_results, last_assessment_time
    
    if assessment_results is None:
        return jsonify({
            'error': 'No assessment results available',
            'message': 'Run an assessment first'
        }), 404
    
    try:
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if report_type == 'csv':
            # Generate CSV report
            report_file = os.path.join(reports_dir, f"assessment_report_{timestamp}.csv")
            report_generator = ReportGenerator(assessment_results)
            report_generator.generate_csv_report(report_file)
            
            return send_file(
                report_file,
                as_attachment=True,
                download_name=f"ad_assessment_{timestamp}.csv",
                mimetype='text/csv'
            )
            
        elif report_type == 'pdf':
            # Generate PDF report
            report_file = os.path.join(reports_dir, f"assessment_report_{timestamp}.pdf")
            report_generator = ReportGenerator(assessment_results)
            report_generator.generate_pdf_report(report_file)
            
            return send_file(
                report_file,
                as_attachment=True,
                download_name=f"ad_assessment_{timestamp}.pdf",
                mimetype='application/pdf'
            )
            
        else:
            return jsonify({
                'error': 'Invalid report type',
                'message': 'Report type must be "csv" or "pdf"'
            }), 400
            
    except Exception as e:
        logger.error(f"Error generating {report_type} report: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Failed to generate {report_type} report',
            'message': str(e)
        }), 500

@app.route('/api/assessment/run-interactive', methods=['POST'])
def run_interactive_assessment():
    """Run main.py in interactive mode with the provided configuration."""
    global assessment_results, last_assessment_time
    
    try:
        # Get configuration from request
        config_data = request.json
        
        # Update configuration
        if config_data:
            config_manager.update_config(config_data)
        
        # Get the current configuration
        config = config_manager.get_config()
        
        # Prepare command to run main.py in interactive mode
        cmd = [
            sys.executable,
            'main.py',
            '--interactive',
            '--save-config'
        ]
        
        # Add additional arguments based on config
        if config.get('domain'):
            cmd.extend(['--domain', config['domain']])
        if config.get('server'):
            cmd.extend(['--server', config['server']])
        if config.get('mock_mode', False):
            cmd.append('--mock')
        if config.get('output_dir'):
            cmd.extend(['--output-dir', config['output_dir']])
        if config.get('verbose', False):
            cmd.append('--verbose')
        
        # Run main.py as a subprocess
        logger.info(f"Starting interactive assessment with command: {' '.join(cmd)}")
        
        # Create a process to run main.py
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        # Collect output
        stdout, stderr = process.communicate()
        
        # Check if process completed successfully
        if process.returncode == 0:
            logger.info("Interactive assessment completed successfully")
            
            # Try to load the latest assessment results
            try:
                # Find the most recent log file
                log_files = [f for f in os.listdir('.') if f.startswith('ad_assessment_') and f.endswith('.log')]
                if log_files:
                    latest_log = max(log_files, key=os.path.getctime)
                    logger.info(f"Found latest log file: {latest_log}")
                
                # Find the most recent report directory
                report_dirs = []
                if os.path.exists('reports'):
                    report_dirs = [os.path.join('reports', d) for d in os.listdir('reports') if os.path.isdir(os.path.join('reports', d))]
                
                if report_dirs:
                    latest_report_dir = max(report_dirs, key=os.path.getctime)
                    logger.info(f"Found latest report directory: {latest_report_dir}")
                    
                    # Try to load assessment results from the report directory
                    json_files = [f for f in os.listdir(latest_report_dir) if f.endswith('.json')]
                    if json_files:
                        latest_json = max([os.path.join(latest_report_dir, f) for f in json_files], key=os.path.getctime)
                        with open(latest_json, 'r') as f:
                            assessment_results = json.load(f)
                            last_assessment_time = datetime.now()
                            logger.info(f"Loaded assessment results from {latest_json}")
            except Exception as e:
                logger.warning(f"Could not load assessment results: {str(e)}")
            
            return jsonify({
                'success': True,
                'message': 'Interactive assessment completed successfully',
                'output': stdout,
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.error(f"Interactive assessment failed with return code {process.returncode}")
            return jsonify({
                'error': 'Interactive assessment failed',
                'message': stderr or 'Unknown error',
                'output': stdout
            }), 500
        
    except Exception as e:
        logger.error(f"Error running interactive assessment: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to run interactive assessment',
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Test connection to domain controllers and return detailed results."""
    try:
        # Get connection parameters from request
        data = request.get_json()
        domain = data.get('domain')
        username = data.get('username')
        password = data.get('password')
        
        if not all([domain, username, password]):
            return jsonify({
                'success': False,
                'error': 'Missing required parameters',
                'details': 'Domain, username, and password are required'
            }), 400

        # Initialize AD connector
        ad_connector = ADConnector(domain, username, password)
        
        # Test basic connection
        connection_result = ad_connector.test_connection()
        
        if not connection_result['success']:
            return jsonify({
                'success': False,
                'error': connection_result['error'],
                'details': connection_result['details'],
                'solutions': connection_result.get('solutions', [])
            }), 400

        # Test domain controller discovery
        dc_result = ad_connector.test_domain_controller_discovery()
        
        if not dc_result['success']:
            return jsonify({
                'success': False,
                'error': dc_result['error'],
                'details': dc_result['details'],
                'solutions': dc_result.get('solutions', [])
            }), 400

        # Test authentication
        auth_result = ad_connector.test_authentication()
        
        if not auth_result['success']:
            return jsonify({
                'success': False,
                'error': auth_result['error'],
                'details': auth_result['details'],
                'solutions': auth_result.get('solutions', [])
            }), 400

        return jsonify({
            'success': True,
            'message': 'All connection tests passed successfully',
            'details': {
                'connection': connection_result,
                'domain_controllers': dc_result,
                'authentication': auth_result
            }
        })

    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e),
            'solutions': [
                'Check if the domain controller is accessible',
                'Verify network connectivity',
                'Ensure the service account has proper permissions'
            ]
        }), 500

def load_sample_data():
    """Load sample assessment results for development."""
    global assessment_results, last_assessment_time
    
    sample_data_path = os.path.join(os.path.dirname(__file__), 'sample_data', 'assessment_results.json')
    
    try:
        if os.path.exists(sample_data_path):
            with open(sample_data_path, 'r') as f:
                assessment_results = json.load(f)
                last_assessment_time = datetime.now()
                logger.info(f"Loaded sample data from {sample_data_path}")
        else:
            logger.warning(f"Sample data file not found: {sample_data_path}")
    except Exception as e:
        logger.error(f"Error loading sample data: {str(e)}", exc_info=True)

def main():
    """Main entry point for the API server."""
    parser = argparse.ArgumentParser(description='Active Directory Security Assessment API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--load-sample-data', action='store_true', help='Load sample assessment results')
    
    args = parser.parse_args()
    
    if args.load_sample_data:
        load_sample_data()
    
    logger.info(f"Starting API server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()
