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
from werkzeug.utils import secure_filename
from pathlib import Path
import time
import traceback  # Add traceback for better error reporting

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
assessment_progress = {
    'isRunning': False,
    'percentComplete': 0,
    'currentTask': '',
    'startTime': None,
    'estimatedCompletion': None
}
assessment_history = []

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

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Handle user registration"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        # Check if username already exists
        auth_config = load_auth_config()
        if auth_config['username'] == username:
            return jsonify({'error': 'Username already exists'}), 400

        # Create new user
        auth_config['username'] = username
        auth_config['password_hash'] = generate_password_hash(password)
        auth_config['password_changed'] = True
        save_auth_config(auth_config)
        
        return jsonify({
            'message': 'User registered successfully'
        }), 200

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

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

@app.route('/api/assessment/progress', methods=['GET'])
@login_required
def get_assessment_progress():
    """Get the current assessment progress."""
    global assessment_progress
    return jsonify(assessment_progress)

@app.route('/api/assessment/history', methods=['GET'])
@login_required
def get_assessment_history():
    """Get the assessment history."""
    global assessment_history
    return jsonify(assessment_history)

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
        global assessment_results, last_assessment_time, assessment_progress, assessment_history
        
        # Update assessment progress
        assessment_progress = {
            'isRunning': True,
            'percentComplete': 0,
            'currentTask': 'Initializing assessment...',
            'startTime': datetime.utcnow().isoformat(),
            'estimatedCompletion': None
        }
        
        # Validate request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No configuration provided'}), 400

        # Get the current configuration
        config = config_manager.get_config()
        
        # Initialize AD connector with the configuration
        ad_connector = ADConnector(config)
        
        # Run assessment
        assessment = SecurityAssessment(ad_connector, config)
        results = assessment.run_assessment()
        
        if not results:
            return jsonify({'error': 'Assessment failed to produce results'}), 500
            
        # Store results
        assessment_results = results
        last_assessment_time = datetime.utcnow()
        
        # Update assessment progress
        assessment_progress = {
            'isRunning': False,
            'percentComplete': 100,
            'currentTask': 'Assessment completed',
            'startTime': assessment_progress['startTime'],
            'estimatedCompletion': datetime.utcnow().isoformat()
        }
        
        # Add to assessment history
        assessment_history.append({
            'id': len(assessment_history) + 1,
            'timestamp': last_assessment_time.isoformat(),
            'domain': config.get('domain', 'Unknown'),
            'compliance_percentage': results.get('summary', {}).get('compliance_percentage', 0),
            'passed_checks': results.get('summary', {}).get('passed', 0),
            'failed_checks': results.get('summary', {}).get('failed', 0)
        })
        
        # Keep only the last 10 assessments in history
        if len(assessment_history) > 10:
            assessment_history = assessment_history[-10:]
        
        return jsonify({
            'message': 'Assessment completed successfully',
            'results': results,
            'timestamp': last_assessment_time.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Assessment error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Assessment failed',
            'message': f'Failed to complete the security assessment: {str(e)}'
        }), 500

@app.route('/api/domain-controllers', methods=['GET'])
@login_required
def get_domain_controllers():
    """Get list of domain controllers."""
    try:
        # Get the current configuration
        config = config_manager.get_config()
        
        # Initialize AD connector with the configuration
        connector = ADConnector(config)
        
        # Connect to AD
        connector.connect()
        
        controllers = connector.get_domain_controllers()
        return jsonify({'domain_controllers': controllers})
    except Exception as e:
        logger.error(f"Failed to get domain controllers: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to retrieve domain controllers',
            'message': f'Could not connect to Active Directory: {str(e)}'
        }), 500

@app.route('/api/computers', methods=['GET'])
@login_required
def get_computers():
    """Get list of computers in the domain."""
    try:
        # Get the current configuration
        config = config_manager.get_config()
        
        # Initialize AD connector with the configuration
        connector = ADConnector(config)
        
        # Connect to AD
        connector.connect()
        
        computers = connector.get_computers()
        return jsonify({'computers': computers})
    except Exception as e:
        logger.error(f"Failed to get computers: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to retrieve computers',
            'message': f'Could not connect to Active Directory: {str(e)}'
        }), 500

@app.route('/api/domain-policies', methods=['GET'])
@login_required
def get_domain_policies():
    """Get domain policies."""
    try:
        # Get the current configuration
        config = config_manager.get_config()
        
        # Initialize AD connector with the configuration
        connector = ADConnector(config)
        
        # Connect to AD
        connector.connect()
        
        policies = connector.get_domain_policies()
        return jsonify({'policies': policies})
    except Exception as e:
        logger.error(f"Failed to get domain policies: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to retrieve domain policies',
            'message': f'Could not connect to Active Directory: {str(e)}'
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
            
        # Get report format from query parameters
        report_format = request.args.get('format', 'pdf')
        
        # Validate report type
        valid_report_types = ['technical', 'executive', 'json']
        if report_type not in valid_report_types:
            return jsonify({
                'error': 'Invalid report type',
                'message': f'Supported types: {", ".join(valid_report_types)}'
            }), 400
            
        # Validate report format
        valid_formats = ['pdf', 'csv']
        if report_format not in valid_formats and report_type != 'json':
            return jsonify({
                'error': 'Invalid report format',
                'message': f'Supported formats: {", ".join(valid_formats)}'
            }), 400
            
        generator = ReportGenerator(assessment_results)
        
        if report_type == 'json':
            return jsonify(assessment_results)
        elif report_format == 'pdf':
            report_path = generator.generate_pdf(report_type)
            return send_file(
                report_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'ad_assessment_{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            )
        else:  # csv
            report_path = generator.generate_csv(report_type)
            return send_file(
                report_path,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'ad_assessment_{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
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

@app.route('/api/reports/<report_type>/preview', methods=['GET'])
@login_required
def get_report_preview(report_type):
    """Generate and return a report preview."""
    try:
        if not assessment_results:
            return jsonify({
                'error': 'No assessment results available',
                'message': 'Run an assessment first'
            }), 400
            
        # Get preview format from query parameters
        preview_format = request.args.get('format', 'html')
        
        # Validate report type
        valid_report_types = ['technical', 'executive']
        if report_type not in valid_report_types:
            return jsonify({
                'error': 'Invalid report type',
                'message': f'Supported types: {", ".join(valid_report_types)}'
            }), 400
            
        # Validate preview format
        valid_formats = ['html', 'json']
        if preview_format not in valid_formats:
            return jsonify({
                'error': 'Invalid preview format',
                'message': f'Supported formats: {", ".join(valid_formats)}'
            }), 400
            
        generator = ReportGenerator(assessment_results)
        preview_content = generator.generate_report_preview(report_type, preview_format)
        
        if preview_format == 'html':
            return jsonify({'html': preview_content})
        else:  # json
            return jsonify(preview_content)
            
    except Exception as e:
        logger.error(f"Failed to generate {report_type} report preview: {str(e)}")
        return jsonify({
            'error': f'Failed to generate {report_type} report preview',
            'message': 'Could not generate the requested preview'
        }), 500

@app.route('/api/baselines', methods=['GET'])
@login_required
def get_baselines():
    """Get available baselines."""
    try:
        # Get baselines directory
        baselines_dir = os.path.join(os.path.dirname(__file__), 'baselines')
        
        # Get list of baseline files
        baseline_files = []
        if os.path.exists(baselines_dir):
            baseline_files = [f for f in os.listdir(baselines_dir) if f.endswith('.json')]
        
        # Get custom baselines directory
        custom_baselines_dir = os.path.join(os.path.dirname(__file__), 'baselines', 'custom')
        
        # Get list of custom baseline files
        custom_baseline_files = []
        if os.path.exists(custom_baselines_dir):
            custom_baseline_files = [f for f in os.listdir(custom_baselines_dir) if f.endswith('.json') or f.endswith('.csv') or f.endswith('.pdf')]
        
        # Prepare response
        baselines = []
        
        # Add built-in baselines
        for file in baseline_files:
            baseline_path = os.path.join(baselines_dir, file)
            try:
                with open(baseline_path, 'r') as f:
                    baseline_data = json.load(f)
                    baselines.append({
                        'id': file.replace('.json', ''),
                        'name': baseline_data.get('name', file.replace('.json', '')),
                        'description': baseline_data.get('description', ''),
                        'type': 'built-in',
                        'file': file
                    })
            except Exception as e:
                logger.error(f"Error loading baseline {file}: {str(e)}")
        
        # Add custom baselines
        for file in custom_baseline_files:
            file_ext = os.path.splitext(file)[1].lower()
            baselines.append({
                'id': f"custom/{file}",
                'name': file,
                'description': f"Custom baseline ({file_ext[1:]} format)",
                'type': 'custom',
                'file': f"custom/{file}"
            })
        
        return jsonify({'baselines': baselines})
    except Exception as e:
        logger.error(f"Failed to get baselines: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve baselines',
            'message': 'Could not load baseline files'
        }), 500

@app.route('/api/baselines/custom', methods=['POST'])
@login_required
def upload_custom_baseline():
    """Upload a custom baseline."""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'message': 'Please provide a file'
            }), 400
        
        file = request.files['file']
        
        # Check if file is empty
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a file'
            }), 400
        
        # Check file extension
        allowed_extensions = {'json', 'csv', 'pdf'}
        file_ext = os.path.splitext(file.filename)[1][1:].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': 'Invalid file type',
                'message': f'Allowed file types: {", ".join(allowed_extensions)}'
            }), 400
        
        # Create custom baselines directory if it doesn't exist
        custom_baselines_dir = os.path.join(os.path.dirname(__file__), 'baselines', 'custom')
        os.makedirs(custom_baselines_dir, exist_ok=True)
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(custom_baselines_dir, filename)
        file.save(file_path)
        
        # Validate JSON files
        if file_ext == 'json':
            try:
                with open(file_path, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError:
                os.remove(file_path)
                return jsonify({
                    'error': 'Invalid JSON file',
                    'message': 'The uploaded file is not a valid JSON file'
                }), 400
        
        return jsonify({
            'message': 'Baseline uploaded successfully',
            'baseline': {
                'id': f"custom/{filename}",
                'name': filename,
                'description': f"Custom baseline ({file_ext} format)",
                'type': 'custom',
                'file': f"custom/{filename}"
            }
        })
    except Exception as e:
        logger.error(f"Failed to upload custom baseline: {str(e)}")
        return jsonify({
            'error': 'Failed to upload custom baseline',
            'message': 'Could not save the uploaded file'
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
        server = data.get('server', '')
        use_ssl = data.get('use_ssl', False)
        port = data.get('port', 389)
        
        if not all([domain, username, password]):
            return jsonify({
                'success': False,
                'error': 'Missing required parameters',
                'details': 'Domain, username, and password are required'
            }), 400

        # Create a config dictionary
        config = {
            'domain': domain,
            'server': server,
            'username': username,
            'password': password,
            'use_ssl': use_ssl,
            'verify_ssl': data.get('verify_ssl', True),
            'port': port if port else (636 if use_ssl else 389),
            'mock_mode': data.get('mock_mode', False)
        }

        logger.info(f"Testing connection to domain: {domain}, server: {server or 'auto-discover'}, port: {config['port']}, use_ssl: {use_ssl}")

        # Initialize AD connector with the configuration
        ad_connector = ADConnector(config)
        
        # Connect to AD
        try:
            connection_success = ad_connector.connect()
            
            if not connection_success:
                return jsonify({
                    'success': False,
                    'error': 'Connection failed',
                    'details': 'Failed to connect to Active Directory',
                    'solutions': [
                        'Check if the domain controller is accessible',
                        'Verify network connectivity',
                        'Ensure the service account has proper permissions',
                        'If using SSL/TLS, verify certificates are valid',
                        'Try using a different port (389 for LDAP, 636 for LDAPS)'
                    ]
                }), 400
        except Exception as conn_error:
            logger.error(f"Connection error: {str(conn_error)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'Connection error',
                'details': str(conn_error),
                'solutions': [
                    'Check if the domain controller is accessible',
                    'Verify network connectivity',
                    'Ensure the service account has proper permissions',
                    'If using SSL/TLS, verify certificates are valid',
                    'Try using a different port (389 for LDAP, 636 for LDAPS)'
                ]
            }), 400
        
        # Get domain controllers to verify connection
        try:
            controllers = ad_connector.get_domain_controllers()
            
            # Prepare detailed test results
            test_results = {
                'connection': {
                    'status': 'Success',
                    'details': f"Connected to {'LDAPS' if use_ssl else 'LDAP'} on port {config['port']}"
                },
                'domain_controllers': {
                    'status': 'Success',
                    'count': len(controllers),
                    'controllers': controllers
                },
                'authentication': {
                    'status': 'Success',
                    'username': username
                }
            }
            
            return jsonify({
                'success': True,
                'message': f"Successfully connected to {domain}" + (f" via {server}" if server else ""),
                'details': test_results
            })
        except Exception as e:
            logger.error(f"Error getting domain controllers: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'Connection verification failed',
                'details': f'Could not retrieve domain controllers: {str(e)}',
                'solutions': [
                    'Check if the domain controller is accessible',
                    'Verify network connectivity',
                    'Ensure the service account has proper permissions',
                    'Check if the account has sufficient privileges to query domain controllers'
                ]
            }), 400

    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e),
            'solutions': [
                'Check if the domain controller is accessible',
                'Verify network connectivity',
                'Ensure the service account has proper permissions',
                'Check the API server logs for more details'
            ]
        }), 500

def load_sample_data():
    """Load sample assessment results for development."""
    global assessment_results, last_assessment_time, assessment_history
    
    sample_data_path = os.path.join(os.path.dirname(__file__), 'sample_data', 'assessment_results.json')
    
    try:
        if os.path.exists(sample_data_path):
            with open(sample_data_path, 'r') as f:
                assessment_results = json.load(f)
                last_assessment_time = datetime.now()
                logger.info(f"Loaded sample data from {sample_data_path}")
                
                # Create sample assessment history
                assessment_history = []
                for i in range(5):
                    days_ago = timedelta(days=i*3)
                    timestamp = datetime.now() - days_ago
                    compliance = max(60, 100 - i*8)  # Decreasing compliance over time
                    passed = int(assessment_results.get('summary', {}).get('total_checks', 100) * compliance / 100)
                    failed = assessment_results.get('summary', {}).get('total_checks', 100) - passed
                    
                    assessment_history.append({
                        'id': 5 - i,
                        'timestamp': timestamp.isoformat(),
                        'domain': assessment_results.get('domain', 'example.com'),
                        'compliance_percentage': compliance,
                        'passed_checks': passed,
                        'failed_checks': failed
                    })
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
