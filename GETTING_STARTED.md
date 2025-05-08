# Getting Started Guide

This guide provides detailed instructions for setting up and running the Active Directory Security Assessment Tool.

## Prerequisites

### System Requirements
- Windows 10/11 or Windows Server 2016/2019/2022
- Python 3.8 or higher
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
copy config.example.json config.json
```

2. Edit `config.json` with your environment settings:
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

## Starting the Application

### Development Environment

#### Option 1: Using the Batch Scripts (Recommended for Windows)

1. Start both the API server and Web UI using the provided batch script:
```bash
# Using the batch script (recommended for Windows)
run_web_ui.bat
# OR
start_web_ui.bat
```

This will:
- Check for required dependencies
- Install Python packages if needed
- Install Node.js packages for the frontend
- Start the API server on port 5000
- Start the Web UI on port 3000

2. Access the web interface:
- API server: http://localhost:5000/api
- Web UI: http://localhost:3000
- Default username: "Orunmila"
- You'll be prompted to create a password on first login

#### Option 2: Manual Startup

1. Start the API server using the run script:
```bash
# Using the run script
python run_api.py
# OR
python api_server.py --host localhost --port 5000 --debug --load-sample-data

# For debugging
python run_api.py --debug
```

2. Start the Web UI:
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies if needed
npm install --force

# Start the development server
npm start
```

3. Access the web interface:
- API server: http://localhost:5000/api
- Web UI: http://localhost:3000
- Default username: "Orunmila"
- You'll be prompted to create a password on first login

### Production Environment

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

## First-Time Setup

1. Access the web interface at http://localhost:5000

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

1. **ModuleNotFoundError**
   ```
   Solution:
   - Ensure you're in the project root directory
   - Verify virtual environment is activated
   - Run the application using run_api.py
   ```

2. **Connection Errors**
   ```
   Solutions:
   - Check network connectivity to domain controllers
   - Verify DNS resolution
   - Ensure firewall rules allow connection
   ```

3. **Authentication Issues**
   ```
   Solutions:
   - Verify service account credentials
   - Check account lockout status
   - Ensure required permissions are granted
   ```

4. **Web UI Not Opening on Port 3000**
   ```
   Solutions:
   - Ensure Node.js and npm are installed and in your PATH
   - Check if the frontend dependencies are installed correctly
   - Run 'cd frontend && npm install --force' to reinstall dependencies
   - Verify there are no other processes using port 3000
   - Use the updated run_web_ui.bat or start_web_ui.bat scripts
   ```

5. **API Server Internal Server Error**
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

## Support

For additional support:
1. Check the [GitHub Issues](https://github.com/manabouprj/ad-security-assessment/issues)
2. Review the [Wiki](https://github.com/manabouprj/ad-security-assessment/wiki)
3. Submit new issues for bugs or feature requests
