# Active Directory Security Assessment Tool

A comprehensive tool for assessing the security posture of Active Directory environments against industry-standard compliance benchmarks.

## Features

- **Baseline Compliance Selection**: Choose from CIS benchmarks, STIG benchmarks, Microsoft Security benchmarks, or upload custom compliance benchmarks in CSV or PDF format.
- **Detailed Assessment Reports**: Get comprehensive reports on your Active Directory security posture.
- **Remediation Steps**: View detailed remediation steps for all failed compliance checks in the technical report.
- **Report Preview**: Preview technical or executive reports before downloading them.
- **Multiple Report Formats**: Download reports in PDF or CSV format.
- **Dashboard**: View assessment results, compliance trends, and key metrics.

## Getting Started

### Prerequisites

- Windows 10/11 or Windows Server 2016/2019/2022
- Python 3.8 or higher
- Node.js 14 or higher
- npm 6 or higher

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/manabouprj/ad-security-assessment.git
   cd ad-security-assessment
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

For the easiest startup experience, use the provided batch file:

```
start_all.bat
```

This will:
1. Install required Python packages
2. Start the API server with sample data
3. Start the frontend development server

Alternatively, you can start the components manually:

1. Start the API server:
   ```
   python run_api.py --load-sample-data
   ```

2. Start the frontend:
   ```
   cd frontend
   npm start
   ```

3. Access the application at http://localhost:3000

## Using the Application

### Login

- Default username: `Orunmila`
- On first login, you'll be prompted to create a password

### Running an Assessment

1. Navigate to the "Run Assessment" page
2. Select a compliance baseline from the available options:
   - CIS Benchmarks
   - STIG Benchmarks
   - Microsoft Security Benchmarks
   - Custom Baselines (uploaded by users)
3. Configure assessment parameters
4. Click "Start Assessment"

### Viewing Results

1. Navigate to the "Assessment Results" page
2. View the overall compliance score and detailed findings
3. Click on individual checks to see remediation steps for failed items

### Generating Reports

1. From the "Assessment Results" page, click "Generate Report"
2. Select the report type (Technical or Executive)
3. Preview the report in the browser
4. Download the report in your preferred format (PDF or CSV)

## Troubleshooting

### "No benchmarks available" Error

If you see "No benchmarks available" in the compliance baselines section:

1. Make sure the API server is running:
   ```
   python run_api.py --load-sample-data
   ```

2. Check if the required Python packages are installed:
   ```
   pip install flask flask-cors werkzeug
   pip install -r requirements.txt
   ```

3. Verify that the baseline JSON files exist in the `baselines` directory

### Other Common Issues

For other common issues, refer to the `UPDATE_GUIDE.md` file for troubleshooting tips.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
