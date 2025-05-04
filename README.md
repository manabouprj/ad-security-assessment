# Active Directory Security Assessment Tool

A comprehensive web-based tool for conducting security assessments of Active Directory environments. This tool helps security professionals and system administrators evaluate their AD infrastructure against security best practices and Microsoft Security Configuration Toolkit standards.

## Key Features
- 🔒 Secure web-based interface for AD security assessment
- 🔑 Role-based access control with password protection
- 📊 Detailed assessment reports and recommendations
- ⚙️ Highly configurable assessment parameters
- 🔄 Mock mode for testing and development
- 📝 Comprehensive logging and audit trails

## Quick Start

For detailed setup and running instructions, please see [GETTING_STARTED.md](GETTING_STARTED.md).

### Basic Setup

```bash
# Clone the repository
git clone https://github.com/manabouprj/ad-security-assessment.git
cd ad-security-assessment

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows PowerShell

# Install package and dependencies
python -m pip install --upgrade pip
pip install -e .

# Set up package structure
python setup_package.py

# Configure the application
copy config.example.json config.json
```

### Running the Application

```bash
# Start the API server (recommended method)
python run_api.py
```

Access the web interface at http://localhost:5000

Default credentials:
- Username: "Orunmila"
- You'll be prompted to create a secure password on first login

## Prerequisites
- Python 3.8 or higher
- Windows environment (for AD integration)
- Network access to domain controllers (for production use)
- Local administrator rights (for installation)

## Security Considerations

### Production Deployment
- Change the default username and password
- Enable HTTPS using a valid SSL certificate
- Configure proper firewall rules
- Use a production-grade WSGI server (e.g., Gunicorn)
- Set up proper backup procedures for assessment data

### Access Control
- Use service accounts with minimum required permissions
- Enable audit logging
- Regularly rotate passwords
- Monitor access logs

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify network connectivity to domain controllers
   - Check service account permissions
   - Ensure proper DNS resolution

2. **Authentication Issues**
   - Verify service account credentials
   - Check for password expiration
   - Ensure proper group memberships

3. **Assessment Failures**
   - Check network timeouts
   - Verify access permissions
   - Review error logs in the `logs` directory

### Debug Mode
For troubleshooting, enable debug mode:
```bash
python api_server.py --debug
```

## Development

### Setting Up Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Run unit tests
python -m pytest tests/

# Run with mock mode
python api_server.py --mock
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[MIT License](LICENSE)

## Authors
[Your Organization/Name]

## Support
For issues and feature requests, please use the [GitHub Issues](https://github.com/manabouprj/ad-security-assessment/issues) page.

## Acknowledgments
- Microsoft Security Configuration Toolkit
- Active Directory PowerShell Module
- Flask and React communities
