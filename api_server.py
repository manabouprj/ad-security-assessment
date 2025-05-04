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
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_file, Response, session
from flask_cors import CORS
from src.core.security_assessment import SecurityAssessment
from src.core.ad_connector import ADConnector
from src.config.config_manager import ConfigManager
from src.reports.report_generator import ReportGenerator
from functools import wraps
import hashlib
import re
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
import time

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load secret key from file or create a new one
SECRET_KEY_FILE = Path(os.path.dirname(os.path.abspath(__file__))) / '.secret_key'
try:
    if SECRET_KEY_FILE.exists():
        app.secret_key = SECRET_KEY_FILE.read_bytes()
    else:
        app.secret_key = os.urandom(24)
        SECRET_KEY_FILE.write_bytes(app.secret_key)
except Exception as e:
    logger.error(f"Error handling secret key: {e}")
    app.secret_key = os.urandom(24)  # Fallback to random key

# Session configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
)

CORS(app, supports_credentials=True)

# Global variables
config_manager = ConfigManager('config.json')
assessment_results = None
last_assessment_time = None

# Authentication configuration
AUTH_FILE = Path(os.path.dirname(os.path.abspath(__file__))) / 'auth_config.json'
DEFAULT_USERNAME = 'Orunmila'
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT = 300  # 5 minutes in seconds

# Store login attempts
login_attempts = {}

def load_auth_config():
    """Load authentication configuration from file"""
    try:
        if AUTH_FILE.exists():
            with open(AUTH_FILE, 'r') as f:
                config = json.load(f)
                if not config or not isinstance(config, dict):
                    config = create_default_auth_config()
                # Ensure all required fields exist
                for field in ['username', 'password_hash', 'password_changed']:
                    if field not in config:
                        config.update(create_default_auth_config())
                        break
                return config
        else:
            config = create_default_auth_config()
            save_auth_config(config)
            return config
    except Exception as e:
        logger.error(f"Error loading auth config: {e}")
        return create_default_auth_config()

def create_default_auth_config():
    """Create default authentication configuration"""
    return {
        'username': DEFAULT_USERNAME,
        'password_hash': None,
        'password_changed': False
    }

def save_auth_config(config):
    """Save authentication configuration to file"""
    try:
        AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(AUTH_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        # Set secure file permissions
        if os.name != 'nt':  # Not Windows
            os.chmod(AUTH_FILE, 0o600)
        logger.info(f"Auth config saved to {AUTH_FILE}")
    except Exception as e:
        logger.error(f"Error saving auth config: {e}")
        raise

def check_login_attempts(username):
    """Check if user has exceeded maximum login attempts"""
    now = time.time()
    if username in login_attempts:
        attempts, timestamp = login_attempts[username]
        if attempts >= MAX_LOGIN_ATTEMPTS:
            if now - timestamp < LOGIN_TIMEOUT:
                return False
            login_attempts[username] = (0, now)
    return True

def record_login_attempt(username, success):
    """Record login attempt for rate limiting"""
    now = time.time()
    if success:
        login_attempts.pop(username, None)
    else:
        attempts, _ = login_attempts.get(username, (0, now))
        login_attempts[username] = (attempts + 1, now)

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

        # Check login attempts
        if not check_login_attempts(username):
            return jsonify({
                'error': 'Too many login attempts. Please try again later.'
            }), 429

        auth_config = load_auth_config()
        if not auth_config:
            logger.error("Failed to load authentication configuration")
            return jsonify({'error': 'Internal server error'}), 500

        if username != auth_config['username']:
            record_login_attempt(username, False)
            return jsonify({'error': 'Invalid credentials'}), 401

        # First login handling
        if auth_config['password_hash'] is None:
            is_valid, error_message = validate_password(password)
            if not is_valid:
                return jsonify({'error': error_message}), 400

            auth_config['password_hash'] = generate_password_hash(password)
            auth_config['password_changed'] = True
            save_auth_config(auth_config)
            
            session.permanent = True
            session['authenticated'] = True
            session['username'] = username
            session['password_changed'] = True
            
            record_login_attempt(username, True)
            return jsonify({
                'message': 'Password created successfully',
                'password_changed': True
            }), 200

        # Normal login
        if check_password_hash(auth_config['password_hash'], password):
            session.permanent = True
            session['authenticated'] = True
            session['username'] = username
            session['password_changed'] = auth_config['password_changed']
            session['last_activity'] = datetime.utcnow().timestamp()
            
            record_login_attempt(username, True)
            return jsonify({
                'message': 'Login successful',
                'password_changed': auth_config['password_changed']
            }), 200
        
        record_login_attempt(username, False)
        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    try:
        username = session.get('username')
        if username:
            login_attempts.pop(username, None)
        session.clear()
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/change-password', methods=['POST'])
@login_required
def change_password():
    """Handle password change."""
    try:
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
            
            # Invalidate all sessions
            session.clear()
            
            return jsonify({'message': 'Password changed successfully. Please login again.'}), 200
        else:
            return jsonify({'error': 'Current password is incorrect'}), 401
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    try:
        auth_config = load_auth_config()
        if not auth_config:
            logger.error("Failed to load authentication configuration")
            return jsonify({
                'authenticated': False,
                'username': None,
                'password_changed': False,
                'error': 'Configuration error'
            }), 500

        # Check session expiry
        if session.get('authenticated'):
            last_activity = session.get('last_activity')
            if last_activity and time.time() - last_activity > app.config['PERMANENT_SESSION_LIFETIME'].total_seconds():
                session.clear()
                return jsonify({
                    'authenticated': False,
                    'username': None,
                    'password_changed': False,
                    'error': 'Session expired'
                })

        return jsonify({
            'authenticated': session.get('authenticated', False),
            'username': session.get('username'),
            'password_changed': session.get('password_changed', False)
        })
    except Exception as e:
        logger.error(f"Auth status error: {str(e)}")
        return jsonify({
            'authenticated': False,
            'username': None,
            'password_changed': False,
            'error': 'Internal server error'
        }), 500

def update_session_activity():
    """Update last activity timestamp in session"""
    if session.get('authenticated'):
        session['last_activity'] = time.time()

@app.before_request
def before_request():
    """Middleware to handle requests before they are processed"""
    try:
        # Skip for static files and health check
        if request.endpoint and 'static' in request.endpoint or request.path == '/api/health':
            return

        # Update session activity
        update_session_activity()

        # Check session expiry for authenticated routes
        if getattr(request.endpoint, 'login_required', False):
            if not session.get('authenticated'):
                return jsonify({'error': 'Authentication required'}), 401
            
            last_activity = session.get('last_activity')
            if last_activity and time.time() - last_activity > app.config['PERMANENT_SESSION_LIFETIME'].total_seconds():
                session.clear()
                return jsonify({'error': 'Session expired'}), 401

    except Exception as e:
        logger.error(f"Before request error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.after_request
def after_request(response):
    """Middleware to handle responses after they are processed"""
    try:
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    except Exception as e:
        logger.error(f"After request error: {str(e)}")
        return response

@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler"""
    logger.error(f"Unhandled error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
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
    """Run a new security assessment."""
    try:
        global assessment_results, last_assessment_time
        
        # Validate request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No configuration provided'}), 400

        # Run assessment
        assessment = SecurityAssessment()
        results = assessment.run()
        
        if not results:
            return jsonify({'error': 'Assessment failed to produce results'}), 500
            
        # Store results
        assessment_results = results
        last_assessment_time = datetime.utcnow()
        
        return jsonify({
            'message': 'Assessment completed successfully',
            'results': results,
            'timestamp': last_assessment_time.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Assessment error: {str(e)}")
        return jsonify({
            'error': 'Assessment failed',
            'message': 'Failed to complete the security assessment'
        }), 500

@app.route('/api/domain-controllers', methods=['GET'])
@login_required
def get_domain_controllers():
    """Get list of domain controllers."""
    try:
        connector = ADConnector()
        controllers = connector.get_domain_controllers()
        return jsonify({'domain_controllers': controllers})
    except Exception as e:
        logger.error(f"Failed to get domain controllers: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve domain controllers',
            'message': 'Could not connect to Active Directory'
        }), 500

@app.route('/api/computers', methods=['GET'])
@login_required
def get_computers():
    """Get list of computers in the domain."""
    try:
        connector = ADConnector()
        computers = connector.get_computers()
        return jsonify({'computers': computers})
    except Exception as e:
        logger.error(f"Failed to get computers: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve computers',
            'message': 'Could not connect to Active Directory'
        }), 500

@app.route('/api/domain-policies', methods=['GET'])
@login_required
def get_domain_policies():
    """Get domain policies."""
    try:
        connector = ADConnector()
        policies = connector.get_domain_policies()
        return jsonify({'policies': policies})
    except Exception as e:
        logger.error(f"Failed to get domain policies: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve domain policies',
            'message': 'Could not connect to Active Directory'
        }), 500

@app.route('/api/config', methods=['GET'])
@login_required
def get_config():
    """Get current configuration."""
    try:
        config = config_manager.get_config()
        return jsonify({'config': config})
    except Exception as e:
        logger.error(f"Failed to get configuration: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve configuration',
            'message': 'Could not load configuration file'
        }), 500

@app.route('/api/config', methods=['PUT'])
@login_required
def update_config():
    """Update configuration."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No configuration provided'}), 400
            
        # Validate configuration
        if not isinstance(data, dict):
            return jsonify({'error': 'Invalid configuration format'}), 400
            
        config_manager.update_config(data)
        return jsonify({
            'message': 'Configuration updated successfully',
            'config': data
        })
    except Exception as e:
        logger.error(f"Failed to update configuration: {str(e)}")
        return jsonify({
            'error': 'Failed to update configuration',
            'message': 'Could not save configuration file'
        }), 500

@app.route('/api/reports/<report_type>', methods=['GET'])
@login_required
def get_report(report_type):
    """Generate and return a report."""
    try:
        if not assessment_results:
            return jsonify({
                'error': 'No assessment results available',
                'message': 'Run an assessment first'
            }), 400
            
        # Validate report type
        valid_report_types = ['pdf', 'json', 'csv']
        if report_type not in valid_report_types:
            return jsonify({
                'error': 'Invalid report type',
                'message': f'Supported types: {", ".join(valid_report_types)}'
            }), 400
            
        generator = ReportGenerator(assessment_results)
        
        if report_type == 'pdf':
            report_path = generator.generate_pdf()
            return send_file(
                report_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'security_assessment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            )
        elif report_type == 'json':
            return jsonify(assessment_results)
        else:  # csv
            report_path = generator.generate_csv()
            return send_file(
                report_path,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'security_assessment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
            
    except Exception as e:
        logger.error(f"Failed to generate {report_type} report: {str(e)}")
        return jsonify({
            'error': f'Failed to generate {report_type} report',
            'message': 'Could not generate the requested report'
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
