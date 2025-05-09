# Getting Started Guide

This guide provides detailed instructions for setting up and running the Active Directory Security Assessment Tool.

## Prerequisites

### System Requirements
- Windows 10/11 or Windows Server 2016/2019/2022
- Python 3.8 or higher
- Node.js 14.x or higher and npm (for the web UI)
- Git (for cloning the repository)
- Network connectivity to domain controllers (for production use)

### Required Permissions
- Local administrator rights on the assessment machine
- Domain user account with appropriate permissions for AD queries

## Installation Steps

### 1. Clone the Repository
```bash
# Clone the repository
git clone https://github.com/manabouprj/ad-security-assessment.git
cd ad-security-assessment
```

### 2. Set Up Python Virtual Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Windows Command Prompt:
.\venv\Scripts\activate.bat
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies and Package
```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install the package in development mode (this will install all required dependencies)
pip install -e .

# Set up proper package structure (if needed)
python setup_package.py
```

### 4. Configure the Application

1. Create configuration file:
```bash
# Copy example configuration
# On Windows:
copy config.example.json config.json
# On Linux/macOS:
cp config.example.json config.json
```

2. Edit `config.json` with your environment settings:
```json
{
  "domain": "your-domain.com",
  "server": "192.168.1.100",
  "username": "service-account",
  "password": "your-password",
  "use_ssl": false,
  "port": 389,
  "mock_mode": false,
  "output_dir": "reports",
  "verbose": true
}
```

## Starting the Application

### Option 1: Full Web UI (Recommended)

This method starts both the API server and the React frontend development server, providing the complete web interface experience.

#### Windows:
```bash
# Using the simplified batch file (recommended)
start_web_ui.bat

# Or using the original batch file
run_web_ui.bat
```

#### Linux/macOS:
```bash
# Make the script executable (first time only)
chmod +x run_web_ui.sh

# Run the script
./run_web_ui.sh
```

The `start_web_ui.bat` script will:
- Start the API server on port 5000 in a separate window
- Start the React development server on port 3000 in a separate window
- Provide clear status messages and instructions
- Keep both servers running in their own windows for easier monitoring and debugging

The `run_web_ui.bat` script will:
- Check for Node.js and npm
- Install frontend dependencies if needed
- Start the API server on port 5000
- Start the React development server on port 3000

**Access the web interface at: http://localhost:3000**

### Option 2: API Server Only

If you only need the API server (for API testing or custom frontends):

```bash
# Start the API server
python run_api.py
# OR
python api_server.py --host localhost --port 5000 --debug --load-sample-data

# For debugging
python run_api.py --debug
```

**Important Note:** When running only the API server, you can access the API endpoints at http://localhost:5000/api/*, but you cannot access the web interface directly. Attempting to access http://localhost:5000/ will result in a 404 error.

### Option 3: Production Environment

For production deployments:

1. Set secure environment variables:
```bash
# On Windows PowerShell:
$env:FLASK_ENV = "production"
$env:FLASK_DEBUG = "0"
```

2. Use a production WSGI server:
```bash
# Install waitress if not already installed
pip install waitress

# Start the server with waitress
waitress-serve --host=0.0.0.0 --port=5000 --call "api_server:create_app"
```

3. Build and serve the frontend:
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Serve using a production web server like nginx or Apache
```

## First-Time Setup

1. Access the web interface:
   - If using the full Web UI (Option 1): http://localhost:3000
   - If using API server only (Option 2): API endpoints at http://localhost:5000/api/*

2. Log in with default credentials:
   - Username: "Orunmila"
   - You'll be prompted to create a secure password

3. Password requirements:
   - Minimum 12 characters
   - At least 2 uppercase letters
   - At least 3 lowercase letters
   - At least 2 numbers
   - At least 1 special character

## Troubleshooting

### Common Issues and Solutions

1. **ModuleNotFoundError: No module named 'src.reports.report_generator'**
   ```
   Solution:
   - Ensure you have the latest version from GitHub
   - If the error persists, create a file at src/reports/report_generator.py with the following content:
     ```python
     """
     Report Generator

     This module re-exports the ReportGenerator class from the reports package.
     """

     from src.reports import ReportGenerator
     ```
   ```

2. **404 Not Found Error when accessing http://localhost:5000/**
   ```
   Solution:
   - This is expected when running only the API server (Option 2)
   - The API server only serves API endpoints at /api/*
   - To access the web interface, use the full Web UI (Option 1) and access http://localhost:3000
   ```

3. **Web UI Error: "Internal server error"**
   ```
   Solution:
   - Make sure both the API server and frontend server are running
   - Use start_web_ui.bat (recommended on Windows) or run_web_ui.bat (Windows) or run_web_ui.sh (Linux/macOS) to start both servers
   - Access the web interface at http://localhost:3000, not http://localhost:5000
   ```

4. **Node.js service not running on port 3000**
   ```
   Solution:
   - Use the simplified start_web_ui.bat script which starts the frontend server in a separate window
   - This makes it easier to monitor the status of both servers and debug any issues
   - The script ensures that both the API server (port 5000) and frontend server (port 3000) are running correctly
   ```

5. **npm not found or Node.js errors**
   ```
   Solution:
   - Install Node.js and npm from https://nodejs.org/
   - Verify installation with: node --version && npm --version
   - Restart your terminal/command prompt after installation
   ```

6. **Connection Errors**
   ```
   Solutions:
   - Check network connectivity to domain controllers
   - Verify DNS resolution
   - Ensure firewall rules allow connection
   - Use IP addresses instead of hostnames for more reliable connections
   - Try using standard LDAP (port 389) instead of LDAPS if SSL connection fails
   ```

7. **Authentication Issues**
   ```
   Solutions:
   - Verify service account credentials
   - Check account lockout status
   - Ensure required permissions are granted
   ```

8. **Web UI Not Opening on Port 3000**
   ```
   Solutions:
   - Ensure Node.js and npm are installed and in your PATH
   - Check if the frontend dependencies are installed correctly
   - Run 'cd frontend && npm install --force' to reinstall dependencies
   - Verify there are no other processes using port 3000
   - Use the updated run_web_ui.bat or start_web_ui.bat scripts
   ```

9. **API Server Internal Server Error**
   ```
   Solutions:
   - Check if all required Python packages are installed
   - Run 'pip install -r requirements.txt' to ensure all dependencies are installed
   - Look for error messages in the terminal where the API server is running
   - Ensure the sample_data directory exists if using --load-sample-data
   - Verify that config.json exists and is properly formatted
   ```

### Debug Mode
For detailed error messages and debugging:
```bash
python run_api.py --debug
```

### Frontend Debugging
For frontend issues:
```bash
cd frontend
npm start
```
This will start the React development server with detailed error messages in the browser console.

## Security Best Practices

1. **Production Deployment**
   - Use HTTPS with valid SSL certificate
   - Configure proper firewall rules
   - Set up monitoring and logging

2. **Access Control**
   - Change default username after first login
   - Use strong passwords
   - Implement proper backup procedures

3. **Maintenance**
   - Regularly update dependencies
   - Monitor log files
   - Perform regular security audits

## Logging

Logs are stored in the following locations:
- Application logs: `./logs/app.log`
- Assessment logs: `./logs/assessment.log`
- API server logs: `./logs/api.log`
- Frontend logs: Browser console when using development server

## Support

For additional support:
1. Check the [GitHub Issues](https://github.com/manabouprj/ad-security-assessment/issues)
2. Review the [Wiki](https://github.com/manabouprj/ad-security-assessment/wiki)
3. Submit new issues for bugs or feature requests
