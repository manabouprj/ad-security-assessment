# Active Directory Security Assessment Tool

A web-based tool for conducting security assessments of Active Directory environments.

## Features
- Web-based interface for AD security assessment
- Password-protected access
- Configurable assessment parameters
- Mock mode for testing
- Detailed assessment reports

## Prerequisites
- Python 3.8 or higher
- Node.js 14.x or higher
- Windows environment (for AD integration)

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd ad-security-assessment
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the application:
- Copy `config.example.json` to `config.json`
- Update the configuration as needed

## Running the Application

1. Start the Flask backend:
```bash
python api_server.py
```

2. Access the web interface:
- Open your browser and navigate to `http://localhost:5000`
- Default username: "Orunmila"
- Create a password on first login

## Configuration

### config.json
```json
{
  "domain": "",
  "server": "",
  "username": "",
  "password": "",
  "mock_mode": true,
  "output_dir": "reports",
  "verbose": true
}
```

## Security Considerations
- Change the default password upon first login
- Use HTTPS in production
- Configure proper firewall rules
- Follow the principle of least privilege

## Development
- Backend: Flask (Python)
- Frontend: React
- Authentication: Flask-Session
- Database: File-based (JSON)

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[Your chosen license]

## Authors
[Your name/organization]
# ad-security-assessment
