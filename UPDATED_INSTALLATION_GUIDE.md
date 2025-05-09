# Updated Installation Guide for Active Directory Security Assessment Tool

This guide provides a comprehensive, step-by-step process for installing and configuring the Active Directory Security Assessment Tool, addressing common issues and ensuring a smooth setup experience.

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

### 3. Install Dependencies
```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install all required dependencies including testing dependencies
pip install -r requirements.txt

# Verify pytest is installed (required for running tests)
pip show pytest
```

### 4. Set Up Package Structure
```bash
# Set up proper package structure
python setup_package.py
```

### 5. Configure the Application
```bash
# Copy example configuration
# On Windows:
copy config.example.json config.json
# On Linux/macOS:
cp config.example.json config.json

# Edit config.json with your environment settings
# Use a text editor to modify the file with your domain information
```

Example configuration:
```json
{
  "domain": "your-domain.com",
  "server": "dc.your-domain.com",
  "username": "service-account",
  "password": "your-password",
  "mock_mode": false,
  "output_dir": "reports",
  "verbose": true
}
```

### 6. Verify Installation with Tests
```bash
# Run the tests to verify the installation
python run_tests.py
```

If you encounter test failures related to the OS detector, ensure that the OS detector module is correctly extracting Windows client version numbers. The tests should pass after our fixes.

## Running the Application

### Option 1: Using the Simplified Batch Script (Recommended for Windows)
```bash
# Start both the API server and Web UI
start_web_ui.bat
```

This script will:
- Start the API server on port 5000 in a separate window
- Start the React development server on port 3000 in a separate window
- Provide clear status messages and instructions
- Keep both servers running in their own windows for easier monitoring and debugging

### Option 2: Using the Comprehensive Batch Script
```bash
# Start both the API server and Web UI with additional setup
run_web_ui.bat
```

This script will:
- Check for Node.js and npm
- Install frontend dependencies if needed
- Install Python packages if needed
- Start the API server on port 5000
- Start the React development server on port 3000

### Option 3: For Linux/macOS Users
```bash
# Make the script executable (first time only)
chmod +x run_web_ui.sh

# Run the script
./run_web_ui.sh
```

### Option 4: Manual Startup (For Advanced Users)
```bash
# Start the API server
python api_server.py --host localhost --port 5000 --debug --load-sample-data

# In a separate terminal, start the frontend
cd frontend
npm install --force  # Only needed first time or when dependencies change
npm start
```

## Accessing the Application

1. Access the web interface at: http://localhost:3000
2. API endpoints are available at: http://localhost:5000/api/*

3. Log in with default credentials:
   - Username: "Orunmila"
   - You'll be prompted to create a secure password on first login

## Troubleshooting Common Issues

### 1. Missing pytest Module
If you encounter errors about missing pytest module when running tests:
```bash
# Ensure you're in the virtual environment, then install pytest
pip install pytest==7.4.0
```

### 2. OS Detector Issues
If you encounter errors related to the OS detector not correctly extracting Windows client version numbers:
```bash
# The fix has been applied in our latest version, but you can verify by running:
python run_tests.py
```

### 3. ModuleNotFoundError: No module named 'src.reports.report_generator'
```bash
# Create the file if it doesn't exist:
mkdir -p src/reports
echo '"""
Report Generator

This module re-exports the ReportGenerator class from the reports package.
"""

from src.reports import ReportGenerator' > src/reports/report_generator.py
```

### 4. Node.js and npm Issues
```bash
# Verify Node.js and npm are installed
node --version
npm --version

# If not installed, download from https://nodejs.org/
# After installation, restart your terminal/command prompt
```

### 5. Frontend Dependency Issues
```bash
# Navigate to frontend directory
cd frontend

# Clean install dependencies with force flag
npm install --force --no-audit --no-fund
```

### 6. Port Conflicts
```bash
# Check if ports 3000 and 5000 are already in use
# On Windows:
netstat -ano | findstr :3000
netstat -ano | findstr :5000

# On Linux/macOS:
lsof -i :3000
lsof -i :5000

# Kill the processes if needed
# On Windows (replace PID with the actual process ID):
taskkill /F /PID PID

# On Linux/macOS:
kill -9 PID
```

## Advanced Configuration

### Running in Mock Mode
For testing without an actual AD connection:
```bash
# Edit config.json and set mock_mode to true
# Or run the API server with the --mock flag
python api_server.py --mock
```

### Debug Mode
For detailed error messages and debugging:
```bash
python api_server.py --debug
```

### Production Deployment
For production environments:
```bash
# Set environment variables
$env:FLASK_ENV = "production"  # Windows PowerShell
export FLASK_ENV=production    # Linux/macOS

# Use a production WSGI server
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 --call "api_server:create_app"

# Build frontend for production
cd frontend
npm run build
# Serve using a production web server like nginx or Apache
```

## Security Best Practices

1. **Change Default Credentials**
   - Change the default username and password immediately after first login

2. **Use HTTPS in Production**
   - Configure SSL/TLS for all production deployments

3. **Regular Updates**
   - Keep all dependencies updated to patch security vulnerabilities
   - Run `pip install --upgrade -r requirements.txt` regularly

4. **Backup Configuration**
   - Regularly backup your configuration and assessment data

5. **Audit Logging**
   - Review logs regularly for suspicious activity
   - Logs are stored in the `./logs/` directory

## Support and Resources

- GitHub Repository: https://github.com/manabouprj/ad-security-assessment
- Issues and Feature Requests: https://github.com/manabouprj/ad-security-assessment/issues
- Wiki: https://github.com/manabouprj/ad-security-assessment/wiki

For additional support, please submit an issue on GitHub with detailed information about your problem or question.
