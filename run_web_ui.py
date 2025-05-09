#!/usr/bin/env python3
"""
Run the Active Directory Security Assessment Web UI

This script starts both the Flask API server and the React frontend development server.
"""

import os
import sys
import subprocess
import argparse
import time
import logging
import platform
import webbrowser
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_windows():
    """Check if the current platform is Windows."""
    return platform.system().lower() == 'windows'

def run_api_server(host, port, debug, load_sample_data):
    """Run the Flask API server."""
    logger.info(f"Starting API server on {host}:{port}")
    
    cmd = [
        sys.executable, 
        'api_server.py',
        '--host', host,
        '--port', str(port)
    ]
    
    if debug:
        cmd.append('--debug')
    
    if load_sample_data:
        cmd.append('--load-sample-data')
    
    try:
        # Use different shell settings based on platform
        if is_windows():
            process = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        logger.info(f"API server process started with PID {process.pid}")
        return process
    except Exception as e:
        logger.error(f"Failed to start API server: {str(e)}")
        return None

def run_frontend_server(port):
    """Run the React frontend development server."""
    logger.info(f"Starting React frontend server on port {port}")
    
    # Change to the frontend directory
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    
    # Set environment variables for the React app
    env = os.environ.copy()
    env['PORT'] = str(port)
    env['REACT_APP_API_URL'] = f'http://localhost:5000/api'
    
    # First ensure all dependencies are installed
    try:
        logger.info("Installing frontend dependencies...")
        if is_windows():
            install_cmd = 'npm install --force --no-audit --no-fund'
            install_process = subprocess.run(
                install_cmd,
                cwd=frontend_dir,
                env=env,
                shell=True,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:
            install_cmd = ['npm', 'install', '--force', '--no-audit', '--no-fund']
            install_process = subprocess.run(
                install_cmd,
                cwd=frontend_dir,
                env=env,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        if install_process.returncode != 0:
            logger.warning(f"npm install warning: {install_process.stderr}")
        else:
            logger.info("Frontend dependencies installed successfully")
    except Exception as e:
        logger.warning(f"Error installing frontend dependencies: {str(e)}")
    
    # Try to start the frontend server
    try:
        logger.info("Running 'npm start' in frontend directory...")
        
        # Use different commands based on platform
        if is_windows():
            cmd = 'npm start'
            process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                env=env,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            cmd = ['npm', 'start']
            process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        logger.info(f"Frontend server process started with PID {process.pid}")
        return process
    except Exception as e:
        logger.warning(f"Failed to start frontend server using standard method: {str(e)}")
    
    # On Windows, try alternative methods
    if is_windows():
        logger.info("Trying alternative methods to start frontend server on Windows...")
        
        # Method 1: Try using npm.cmd directly
        try:
            npm_cmd = 'npm.cmd'
            logger.info(f"Running '{npm_cmd} start' in frontend directory...")
            
            process = subprocess.Popen(
                [npm_cmd, 'start'],
                cwd=frontend_dir,
                env=env,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            logger.info(f"Frontend server process started with PID {process.pid} using npm.cmd")
            return process
        except Exception as e:
            logger.warning(f"Failed to start frontend server using npm.cmd: {str(e)}")
        
        # Method 2: Try common npm paths
        common_paths = [
            os.path.join(os.environ.get('ProgramFiles', ''), 'nodejs', 'npm.cmd'),
            os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'nodejs', 'npm.cmd'),
            os.path.join(os.environ.get('APPDATA', ''), 'npm', 'npm.cmd'),
            os.path.join(os.environ.get('APPDATA', ''), 'Roaming', 'npm', 'npm.cmd')
        ]
        
        for npm_path in common_paths:
            if os.path.exists(npm_path):
                try:
                    logger.info(f"Running '{npm_path} start' in frontend directory...")
                    
                    process = subprocess.Popen(
                        [npm_path, 'start'],
                        cwd=frontend_dir,
                        env=env,
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                    
                    logger.info(f"Frontend server process started with PID {process.pid} using {npm_path}")
                    return process
                except Exception as e:
                    logger.warning(f"Failed to start frontend server using {npm_path}: {str(e)}")
        
        # Method 3: Try using where.exe to find npm
        try:
            result = subprocess.run(
                ['where', 'npm'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                npm_path = result.stdout.strip().split('\n')[0]
                
                try:
                    logger.info(f"Running '{npm_path} start' in frontend directory...")
                    
                    process = subprocess.Popen(
                        [npm_path, 'start'],
                        cwd=frontend_dir,
                        env=env,
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                    
                    logger.info(f"Frontend server process started with PID {process.pid} using {npm_path}")
                    return process
                except Exception as e:
                    logger.warning(f"Failed to start frontend server using {npm_path}: {str(e)}")
        except Exception as e:
            logger.warning(f"Error using 'where' to find npm: {str(e)}")
        
        # Method 4: Try using Node.js directly to run the start script
        try:
            # First find node
            node_result = subprocess.run(
                ['where', 'node'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if node_result.returncode == 0:
                node_path = node_result.stdout.strip().split('\n')[0]
                
                # Get the start script from package.json
                try:
                    with open(os.path.join(frontend_dir, 'package.json'), 'r') as f:
                        import json
                        package_json = json.load(f)
                        start_script = package_json.get('scripts', {}).get('start', 'react-scripts start')
                    
                    logger.info(f"Running Node.js directly with start script: {start_script}")
                    
                    # Run node with the start script
                    process = subprocess.Popen(
                        [node_path, os.path.join(frontend_dir, 'node_modules', '.bin', 'react-scripts'), 'start'],
                        cwd=frontend_dir,
                        env=env,
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                    
                    logger.info(f"Frontend server process started with PID {process.pid} using Node.js directly")
                    return process
                except Exception as e:
                    logger.warning(f"Failed to start frontend server using Node.js directly: {str(e)}")
        except Exception as e:
            logger.warning(f"Error using 'where' to find node: {str(e)}")
    
    logger.error("Failed to start frontend server after trying multiple methods")
    return None

def check_npm_installed():
    """Check if npm is installed."""
    # First try the standard way
    try:
        logger.info("Checking for npm installation...")
        result = subprocess.run(
            ['npm', '--version'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        if result.returncode == 0:
            npm_version = result.stdout.strip()
            logger.info(f"npm version {npm_version} found")
            return True
        else:
            logger.warning(f"npm check failed with error: {result.stderr.strip()}")
    except FileNotFoundError:
        logger.warning("npm not found in PATH")
    except Exception as e:
        logger.warning(f"Error checking npm: {str(e)}")
    
    # On Windows, try additional methods
    if is_windows():
        logger.info("Trying alternative methods to find npm on Windows...")
        
        # Method 1: Check common installation paths
        common_paths = [
            os.path.join(os.environ.get('ProgramFiles', ''), 'nodejs', 'npm.cmd'),
            os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'nodejs', 'npm.cmd'),
            os.path.join(os.environ.get('APPDATA', ''), 'npm', 'npm.cmd'),
            os.path.join(os.environ.get('APPDATA', ''), 'Roaming', 'npm', 'npm.cmd')
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                logger.info(f"Found npm at: {path}")
                
                # Try to run it to verify
                try:
                    result = subprocess.run(
                        [path, '--version'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False
                    )
                    
                    if result.returncode == 0:
                        npm_version = result.stdout.strip()
                        logger.info(f"npm version {npm_version} found at {path}")
                        
                        # Add the directory to PATH for future use
                        os.environ['PATH'] = os.path.dirname(path) + os.pathsep + os.environ.get('PATH', '')
                        logger.info(f"Added {os.path.dirname(path)} to PATH")
                        
                        return True
                except Exception as e:
                    logger.warning(f"Error running npm from {path}: {str(e)}")
        
        # Method 2: Try using where.exe to find npm
        try:
            result = subprocess.run(
                ['where', 'npm'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                npm_path = result.stdout.strip().split('\n')[0]
                logger.info(f"npm found at: {npm_path}")
                
                # Try to run it to verify
                try:
                    version_result = subprocess.run(
                        [npm_path, '--version'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False
                    )
                    
                    if version_result.returncode == 0:
                        npm_version = version_result.stdout.strip()
                        logger.info(f"npm version {npm_version} found at {npm_path}")
                        
                        # Add the directory to PATH for future use
                        os.environ['PATH'] = os.path.dirname(npm_path) + os.pathsep + os.environ.get('PATH', '')
                        logger.info(f"Added {os.path.dirname(npm_path)} to PATH")
                        
                        return True
                except Exception as e:
                    logger.warning(f"Error running npm from {npm_path}: {str(e)}")
        except Exception as e:
            logger.warning(f"Error using 'where' to find npm: {str(e)}")
        
        # Method 3: Try using Node.js to find npm
        try:
            # First find node
            node_result = subprocess.run(
                ['where', 'node'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if node_result.returncode == 0:
                node_path = node_result.stdout.strip().split('\n')[0]
                logger.info(f"Node.js found at: {node_path}")
                
                # npm is typically in the same directory as node
                npm_path = os.path.join(os.path.dirname(node_path), 'npm.cmd')
                
                if os.path.exists(npm_path):
                    logger.info(f"npm found at: {npm_path}")
                    
                    # Try to run it to verify
                    try:
                        version_result = subprocess.run(
                            [npm_path, '--version'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            check=False
                        )
                        
                        if version_result.returncode == 0:
                            npm_version = version_result.stdout.strip()
                            logger.info(f"npm version {npm_version} found at {npm_path}")
                            
                            # Add the directory to PATH for future use
                            os.environ['PATH'] = os.path.dirname(npm_path) + os.pathsep + os.environ.get('PATH', '')
                            logger.info(f"Added {os.path.dirname(npm_path)} to PATH")
                            
                            return True
                    except Exception as e:
                        logger.warning(f"Error running npm from {npm_path}: {str(e)}")
        except Exception as e:
            logger.warning(f"Error using 'where' to find node: {str(e)}")
    
    logger.error("npm not found after trying multiple methods")
    return False

def install_frontend_dependencies():
    """Install frontend dependencies using npm."""
    logger.info("Installing frontend dependencies...")
    
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    
    # First try the standard way with --force flag and suppressing vulnerability warnings
    try:
        logger.info("Running 'npm install --force --no-audit --no-fund' in frontend directory...")
        result = subprocess.run(
            ['npm', 'install', '--force', '--no-audit', '--no-fund', '--loglevel=error'],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logger.info("Frontend dependencies installed successfully")
            return True
        else:
            logger.warning(f"npm install --force failed with error: {result.stderr.strip()}")
    except Exception as e:
        logger.warning(f"Error running npm install --force: {str(e)}")
    
    # On Windows, try alternative methods
    if is_windows():
        logger.info("Trying alternative methods to install dependencies on Windows...")
        
        # Method 1: Try using npm.cmd directly
        try:
            npm_cmd = 'npm.cmd'
            logger.info(f"Running '{npm_cmd} install --force' in frontend directory...")
            
            result = subprocess.run(
                [npm_cmd, 'install', '--force', '--no-audit', '--no-fund', '--loglevel=error'],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True,
                check=False
            )
            
            if result.returncode == 0:
                logger.info("Frontend dependencies installed successfully using npm.cmd")
                return True
            else:
                logger.warning(f"npm.cmd install --force failed with error: {result.stderr.strip()}")
        except Exception as e:
            logger.warning(f"Error running npm.cmd install --force: {str(e)}")
        
        # Method 2: Try common npm paths
        common_paths = [
            os.path.join(os.environ.get('ProgramFiles', ''), 'nodejs', 'npm.cmd'),
            os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'nodejs', 'npm.cmd'),
            os.path.join(os.environ.get('APPDATA', ''), 'npm', 'npm.cmd'),
            os.path.join(os.environ.get('APPDATA', ''), 'Roaming', 'npm', 'npm.cmd')
        ]
        
        for npm_path in common_paths:
            if os.path.exists(npm_path):
                try:
                    logger.info(f"Running '{npm_path} install --force' in frontend directory...")
                    
                    result = subprocess.run(
                        [npm_path, 'install', '--force', '--no-audit', '--no-fund', '--loglevel=error'],
                        cwd=frontend_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"Frontend dependencies installed successfully using {npm_path}")
                        return True
                    else:
                        logger.warning(f"npm install --force from {npm_path} failed with error: {result.stderr.strip()}")
                except Exception as e:
                    logger.warning(f"Error running npm install --force from {npm_path}: {str(e)}")
        
        # Method 3: Try using where.exe to find npm
        try:
            result = subprocess.run(
                ['where', 'npm'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                npm_path = result.stdout.strip().split('\n')[0]
                
                try:
                    logger.info(f"Running '{npm_path} install --force' in frontend directory...")
                    
                    install_result = subprocess.run(
                        [npm_path, 'install', '--force'],
                        cwd=frontend_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False
                    )
                    
                    if install_result.returncode == 0:
                        logger.info(f"Frontend dependencies installed successfully using {npm_path}")
                        return True
                    else:
                        logger.warning(f"npm install --force from {npm_path} failed with error: {install_result.stderr.strip()}")
                except Exception as e:
                    logger.warning(f"Error running npm install --force from {npm_path}: {str(e)}")
        except Exception as e:
            logger.warning(f"Error using 'where' to find npm: {str(e)}")
        
        # Method 4: Try installing just the missing package directly
        try:
            logger.info("Trying to install react-bootstrap-icons package directly...")
            
            # First try to find npm
            npm_cmd = None
            
            # Try PATH
            try:
                where_result = subprocess.run(
                    ['where', 'npm'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                if where_result.returncode == 0:
                    npm_cmd = where_result.stdout.strip().split('\n')[0]
            except Exception:
                pass
            
            # Try common locations
            if not npm_cmd:
                for path in common_paths:
                    if os.path.exists(path):
                        npm_cmd = path
                        break
            
            # If we found npm, try to install just the missing package
            if npm_cmd:
                logger.info(f"Running '{npm_cmd} install react-bootstrap-icons' in frontend directory...")
                
                install_result = subprocess.run(
                    [npm_cmd, 'install', 'react-bootstrap-icons', '--save', '--no-audit', '--no-fund', '--loglevel=error'],
                    cwd=frontend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                if install_result.returncode == 0:
                    logger.info("react-bootstrap-icons package installed successfully")
                    return True
                else:
                    logger.warning(f"Failed to install react-bootstrap-icons: {install_result.stderr.strip()}")
        except Exception as e:
            logger.warning(f"Error installing react-bootstrap-icons directly: {str(e)}")
    
    logger.error("Failed to install frontend dependencies after trying multiple methods")
    return False

def open_browser(url, delay=5):
    """Open the browser after a delay."""
    def _open_browser():
        time.sleep(delay)
        logger.info(f"Opening browser at {url}")
        webbrowser.open(url)
    
    browser_thread = Thread(target=_open_browser)
    browser_thread.daemon = True
    browser_thread.start()

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Run the Active Directory Security Assessment Web UI')
    parser.add_argument('--api-host', default='localhost', help='API server host')
    parser.add_argument('--api-port', type=int, default=5000, help='API server port')
    parser.add_argument('--frontend-port', type=int, default=3000, help='Frontend server port')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    parser.add_argument('--load-sample-data', action='store_true', help='Load sample assessment results')
    
    args = parser.parse_args()
    
    # Check if npm is installed
    if not check_npm_installed():
        logger.error("npm is not installed. Please install Node.js and npm to run the frontend.")
        return 1
    
    # Install frontend dependencies
    if not install_frontend_dependencies():
        logger.error("Failed to install frontend dependencies. Please check npm and try again.")
        return 1
    
    # Start the API server
    api_process = run_api_server(args.api_host, args.api_port, args.debug, args.load_sample_data)
    if not api_process:
        logger.error("Failed to start API server")
        return 1
    
    # Start the frontend server
    frontend_process = run_frontend_server(args.frontend_port)
    if not frontend_process:
        logger.error("Failed to start frontend server")
        api_process.terminate()
        return 1
    
    # Open browser
    if not args.no_browser:
        frontend_url = f"http://localhost:{args.frontend_port}"
        open_browser(frontend_url)
    
    logger.info("Web UI is now running")
    logger.info(f"API server: http://{args.api_host}:{args.api_port}/api")
    logger.info(f"Frontend: http://localhost:{args.frontend_port}")
    
    try:
        # Keep the script running until Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        # Terminate processes
        if api_process:
            api_process.terminate()
        if frontend_process:
            frontend_process.terminate()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
