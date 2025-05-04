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

1. Start the API server using the run script:
```bash
# Using the run script (recommended)
python run_api.py

# For debugging
python run_api.py --debug
```

2. Access the web interface:
- URL: http://localhost:5000
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