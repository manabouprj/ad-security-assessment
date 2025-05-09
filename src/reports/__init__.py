"""
Report generation modules for CSV and PDF output.
"""

import os
import csv
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates reports based on security assessment results.
    Compatible with the API server interface.
    """
    
    def __init__(self, assessment_results):
        """
        Initialize the report generator with assessment results.
        
        Args:
            assessment_results: Dictionary containing assessment results
        """
        self.assessment_results = assessment_results
        
        # Create a temporary output directory for reports
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                      'reports', 
                                      f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Generate timestamp for filenames
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.domain = assessment_results.get('domain', 'unknown_domain')
        
        # Store report configuration
        self.report_config = assessment_results.get('report_config', {
            'include_remediation': True,
            'include_executive_summary': True,
            'include_charts': True,
            'company_name': 'Your Organization'
        })
        
        logger.debug(f"Initialized report generator for domain: {self.domain}")
    
    def generate_csv(self, report_type='technical'):
        """
        Generate a CSV report of the assessment results.
        
        Args:
            report_type: Type of report to generate ('technical' or 'executive')
            
        Returns:
            Path to the generated CSV file
        """
        logger.info(f"Generating {report_type} CSV report")
        
        # Define CSV filename
        filename = f"ad_assessment_{report_type}_{self.domain}_{self.timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', newline='') as csvfile:
                # Create CSV writer
                csv_writer = csv.writer(csvfile)
                
                if report_type == 'executive':
                    return self._generate_executive_csv(csv_writer, filepath)
                else:
                    return self._generate_technical_csv(csv_writer, filepath)
                
        except Exception as e:
            logger.error(f"Error generating CSV report: {str(e)}", exc_info=True)
            return ""
    
    def _generate_technical_csv(self, csv_writer, filepath):
        """Generate technical CSV report"""
        # Write header
        if self.report_config.get('include_remediation', True):
            csv_writer.writerow([
                'Target', 'Setting Name', 'Setting Path', 'Baseline Value',
                'Actual Value', 'Status', 'Severity', 'Remediation'
            ])
        else:
            csv_writer.writerow([
                'Target', 'Setting Name', 'Setting Path', 'Baseline Value',
                'Actual Value', 'Status', 'Severity'
            ])
        
        # Write domain controller results
        for dc in self.assessment_results.get('domain_controllers', []):
            dc_name = dc.get('name', 'Unknown')
            for result in dc.get('results', []):
                if self.report_config.get('include_remediation', True):
                    csv_writer.writerow([
                        f"DC: {dc_name}",
                        result.get('setting_name', 'Unknown'),
                        result.get('setting_path', 'Unknown'),
                        result.get('baseline_value', 'Unknown'),
                        result.get('actual_value', 'Unknown'),
                        result.get('status', 'Unknown'),
                        result.get('severity', 'Unknown'),
                        self._get_remediation_step(result) if result.get('status') == 'fail' else 'N/A'
                    ])
                else:
                    csv_writer.writerow([
                        f"DC: {dc_name}",
                        result.get('setting_name', 'Unknown'),
                        result.get('setting_path', 'Unknown'),
                        result.get('baseline_value', 'Unknown'),
                        result.get('actual_value', 'Unknown'),
                        result.get('status', 'Unknown'),
                        result.get('severity', 'Unknown')
                    ])
        
        # Write member computer results
        for computer in self.assessment_results.get('computers', []):
            computer_name = computer.get('name', 'Unknown')
            for result in computer.get('results', []):
                if self.report_config.get('include_remediation', True):
                    csv_writer.writerow([
                        f"Computer: {computer_name}",
                        result.get('setting_name', 'Unknown'),
                        result.get('setting_path', 'Unknown'),
                        result.get('baseline_value', 'Unknown'),
                        result.get('actual_value', 'Unknown'),
                        result.get('status', 'Unknown'),
                        result.get('severity', 'Unknown'),
                        self._get_remediation_step(result) if result.get('status') == 'fail' else 'N/A'
                    ])
                else:
                    csv_writer.writerow([
                        f"Computer: {computer_name}",
                        result.get('setting_name', 'Unknown'),
                        result.get('setting_path', 'Unknown'),
                        result.get('baseline_value', 'Unknown'),
                        result.get('actual_value', 'Unknown'),
                        result.get('status', 'Unknown'),
                        result.get('severity', 'Unknown')
                    ])
        
        # Write domain policy results
        if 'password_policy' in self.assessment_results.get('domain_policies', {}):
            for result in self.assessment_results['domain_policies']['password_policy'].get('results', []):
                if self.report_config.get('include_remediation', True):
                    csv_writer.writerow([
                        "Domain Password Policy",
                        result.get('setting_name', 'Unknown'),
                        '',  # No path for domain policies
                        result.get('baseline_value', 'Unknown'),
                        result.get('actual_value', 'Unknown'),
                        result.get('status', 'Unknown'),
                        result.get('severity', 'Unknown'),
                        self._get_remediation_step(result) if result.get('status') == 'fail' else 'N/A'
                    ])
                else:
                    csv_writer.writerow([
                        "Domain Password Policy",
                        result.get('setting_name', 'Unknown'),
                        '',  # No path for domain policies
                        result.get('baseline_value', 'Unknown'),
                        result.get('actual_value', 'Unknown'),
                        result.get('status', 'Unknown'),
                        result.get('severity', 'Unknown')
                    ])
        
        logger.info(f"Technical CSV report generated: {filepath}")
        return filepath
    
    def _generate_executive_csv(self, csv_writer, filepath):
        """Generate executive CSV report"""
        # Write header
        csv_writer.writerow([
            'Category', 'Metric', 'Value'
        ])
        
        # Write summary information
        summary = self.assessment_results.get('summary', {})
        csv_writer.writerow(['Summary', 'Total Checks', summary.get('total_checks', 0)])
        csv_writer.writerow(['Summary', 'Passed Checks', summary.get('passed', 0)])
        csv_writer.writerow(['Summary', 'Failed Checks', summary.get('failed', 0)])
        csv_writer.writerow(['Summary', 'Warning Checks', summary.get('warning', 0)])
        csv_writer.writerow(['Summary', 'Not Applicable Checks', summary.get('not_applicable', 0)])
        csv_writer.writerow(['Summary', 'Compliance Percentage', f"{summary.get('compliance_percentage', 0)}%"])
        
        # Count severity issues
        high_severity = 0
        medium_severity = 0
        low_severity = 0
        
        # Function to count severity issues
        def count_severity(results):
            nonlocal high_severity, medium_severity, low_severity
            for result in results:
                if result.get('status') == 'fail':
                    severity = result.get('severity', '').lower()
                    if severity == 'high':
                        high_severity += 1
                    elif severity == 'medium':
                        medium_severity += 1
                    elif severity == 'low':
                        low_severity += 1
        
        # Count issues from domain controllers
        for dc in self.assessment_results.get('domain_controllers', []):
            count_severity(dc.get('results', []))
        
        # Count issues from computers
        for computer in self.assessment_results.get('computers', []):
            count_severity(computer.get('results', []))
        
        # Count issues from domain policies
        if 'password_policy' in self.assessment_results.get('domain_policies', {}):
            count_severity(self.assessment_results['domain_policies']['password_policy'].get('results', []))
        
        # Write severity breakdown
        csv_writer.writerow(['Severity', 'High Severity Issues', high_severity])
        csv_writer.writerow(['Severity', 'Medium Severity Issues', medium_severity])
        csv_writer.writerow(['Severity', 'Low Severity Issues', low_severity])
        
        # Write key recommendations if available
        if self.assessment_results.get('recommendations'):
            csv_writer.writerow(['', '', ''])  # Empty row as separator
            csv_writer.writerow(['Key Recommendations', 'Severity', 'Target'])
            
            # Sort recommendations by severity
            sorted_recommendations = sorted(
                self.assessment_results.get('recommendations', []),
                key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x.get('severity', 'low'), 3)
            )
            
            # Write top 5 recommendations
            for i, rec in enumerate(sorted_recommendations[:5]):
                csv_writer.writerow([
                    rec.get('recommendation', 'Unknown'),
                    rec.get('severity', 'Unknown').upper(),
                    rec.get('target', 'Unknown')
                ])
        
        logger.info(f"Executive CSV report generated: {filepath}")
        return filepath
    
    def generate_pdf(self, report_type='technical'):
        """
        Generate a PDF report.
        
        Args:
            report_type: Type of report to generate ('technical' or 'executive')
            
        Returns:
            Path to the generated PDF file
        """
        logger.info(f"Generating {report_type} PDF report")
        
        # Define PDF filename
        filename = f"ad_assessment_{report_type}_{self.domain}_{self.timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # In a real implementation, this would use a PDF generation library
            # For now, we'll create a simple HTML file as a placeholder
            html_path = os.path.join(self.output_dir, f"ad_assessment_{report_type}_{self.domain}_{self.timestamp}.html")
            
            if report_type == 'executive':
                self._generate_executive_html(html_path)
            else:
                self._generate_technical_html(html_path)
            
            logger.info(f"{report_type.capitalize()} PDF report placeholder generated: {html_path}")
            return html_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}", exc_info=True)
            return ""
    
    def _generate_technical_html(self, html_path):
        """Generate technical HTML report"""
        # Count failed checks
        failed_checks = []
        
        # Function to collect failed checks
        def collect_failed_checks(results, target):
            for result in results:
                if result.get('status') == 'fail':
                    failed_checks.append({
                        'target': target,
                        'setting_name': result.get('setting_name', 'Unknown'),
                        'setting_path': result.get('setting_path', ''),
                        'baseline_value': result.get('baseline_value', 'Unknown'),
                        'actual_value': result.get('actual_value', 'Unknown'),
                        'severity': result.get('severity', 'Unknown'),
                        'remediation': self._get_remediation_step(result)
                    })
        
        # Collect failed checks from domain controllers
        for dc in self.assessment_results.get('domain_controllers', []):
            dc_name = dc.get('name', 'Unknown')
            collect_failed_checks(dc.get('results', []), f"DC: {dc_name}")
        
        # Collect failed checks from computers
        for computer in self.assessment_results.get('computers', []):
            computer_name = computer.get('name', 'Unknown')
            collect_failed_checks(computer.get('results', []), f"Computer: {computer_name}")
        
        # Collect failed checks from domain policies
        if 'password_policy' in self.assessment_results.get('domain_policies', {}):
            collect_failed_checks(
                self.assessment_results['domain_policies']['password_policy'].get('results', []),
                "Domain Password Policy"
            )
        
        # Sort failed checks by severity
        failed_checks.sort(
            key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x.get('severity', 'low'), 3)
        )
        
        # Generate HTML content
        summary = self.assessment_results.get('summary', {})
        
        with open(html_path, 'w') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Active Directory Security Assessment Technical Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .high {{ color: #e74c3c; }}
        .medium {{ color: #f39c12; }}
        .low {{ color: #27ae60; }}
        .summary-box {{ background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin-bottom: 20px; }}
        .failed-check {{ border-bottom: 1px solid #eee; padding: 10px 0; }}
    </style>
</head>
<body>
    <h1>Active Directory Security Assessment Technical Report</h1>
    <p><strong>Domain:</strong> {self.domain}</p>
    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary-box">
        <h2>Assessment Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Checks</td>
                <td>{summary.get('total_checks', 0)}</td>
            </tr>
            <tr>
                <td>Passed Checks</td>
                <td>{summary.get('passed', 0)}</td>
            </tr>
            <tr>
                <td>Failed Checks</td>
                <td>{summary.get('failed', 0)}</td>
            </tr>
            <tr>
                <td>Warning Checks</td>
                <td>{summary.get('warning', 0)}</td>
            </tr>
            <tr>
                <td>Not Applicable Checks</td>
                <td>{summary.get('not_applicable', 0)}</td>
            </tr>
            <tr>
                <td>Compliance Percentage</td>
                <td>{summary.get('compliance_percentage', 0)}%</td>
            </tr>
        </table>
    </div>
    
    <h2>Failed Checks with Remediation Steps</h2>
""")
            
            if failed_checks:
                for check in failed_checks:
                    severity_class = check.get('severity', 'low').lower()
                    f.write(f"""
    <div class="failed-check">
        <h3 class="{severity_class}">{check['setting_name']} ({check['severity'].upper()})</h3>
        <p><strong>Target:</strong> {check['target']}</p>
        {f'<p><strong>Path:</strong> {check["setting_path"]}</p>' if check['setting_path'] else ''}
        <p><strong>Baseline Value:</strong> {check['baseline_value']}</p>
        <p><strong>Actual Value:</strong> {check['actual_value']}</p>
        <p><strong>Remediation:</strong> {check['remediation']}</p>
    </div>
""")
            else:
                f.write("<p>No failed checks found.</p>")
            
            f.write("""
</body>
</html>""")
    
    def _generate_executive_html(self, html_path):
        """Generate executive HTML report"""
        # Count severity issues
        high_severity = 0
        medium_severity = 0
        low_severity = 0
        
        # Function to count severity issues
        def count_severity(results):
            nonlocal high_severity, medium_severity, low_severity
            for result in results:
                if result.get('status') == 'fail':
                    severity = result.get('severity', '').lower()
                    if severity == 'high':
                        high_severity += 1
                    elif severity == 'medium':
                        medium_severity += 1
                    elif severity == 'low':
                        low_severity += 1
        
        # Count issues from domain controllers
        for dc in self.assessment_results.get('domain_controllers', []):
            count_severity(dc.get('results', []))
        
        # Count issues from computers
        for computer in self.assessment_results.get('computers', []):
            count_severity(computer.get('results', []))
        
        # Count issues from domain policies
        if 'password_policy' in self.assessment_results.get('domain_policies', {}):
            count_severity(self.assessment_results['domain_policies']['password_policy'].get('results', []))
        
        # Generate key findings
        key_findings = []
        
        summary = self.assessment_results.get('summary', {})
        compliance = summary.get('compliance_percentage', 0)
        
        if high_severity > 0:
            key_findings.append(f"{high_severity} high severity issues require immediate attention")
        
        if compliance < 70:
            key_findings.append(f"Overall compliance is below recommended threshold (70%)")
        
        if 'password_policy' in self.assessment_results.get('domain_policies', {}):
            password_policy = self.assessment_results['domain_policies']['password_policy']
            failed_password_policies = [r for r in password_policy.get('results', []) if r.get('status') == 'fail']
            
            if failed_password_policies:
                key_findings.append("Domain password policy does not meet security requirements")
        
        # Get top recommendations
        top_recommendations = []
        if self.assessment_results.get('recommendations'):
            # Sort recommendations by severity
            sorted_recommendations = sorted(
                self.assessment_results.get('recommendations', []),
                key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x.get('severity', 'low'), 3)
            )
            
            # Get top 5 recommendations
            top_recommendations = sorted_recommendations[:5]
        
        # Generate HTML content
        with open(html_path, 'w') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Active Directory Security Assessment Executive Summary</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .high {{ color: #e74c3c; }}
        .medium {{ color: #f39c12; }}
        .low {{ color: #27ae60; }}
        .summary-box {{ background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin-bottom: 20px; }}
        .compliance-indicator {{ 
            height: 20px; 
            background: linear-gradient(to right, #e74c3c, #f39c12, #27ae60);
            position: relative;
            margin: 20px 0;
        }}
        .compliance-marker {{
            position: absolute;
            width: 2px;
            height: 30px;
            background-color: #2c3e50;
            top: -5px;
            left: {compliance}%;
        }}
        .compliance-label {{
            position: absolute;
            top: 25px;
            left: {compliance - 10}%;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>Active Directory Security Assessment Executive Summary</h1>
    <p><strong>Domain:</strong> {self.domain}</p>
    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>Organization:</strong> {self.report_config.get('company_name', 'Your Organization')}</p>
    
    <div class="summary-box">
        <h2>Compliance Overview</h2>
        <p>Overall compliance score: <strong>{compliance}%</strong></p>
        
        <div class="compliance-indicator">
            <div class="compliance-marker"></div>
            <div class="compliance-label">{compliance}%</div>
        </div>
        
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Checks</td>
                <td>{summary.get('total_checks', 0)}</td>
            </tr>
            <tr>
                <td>Passed Checks</td>
                <td>{summary.get('passed', 0)}</td>
            </tr>
            <tr>
                <td>Failed Checks</td>
                <td>{summary.get('failed', 0)}</td>
            </tr>
        </table>
    </div>
    
    <div class="summary-box">
        <h2>Severity Breakdown</h2>
        <table>
            <tr>
                <th>Severity</th>
                <th>Count</th>
                <th>Description</th>
            </tr>
            <tr class="high">
                <td>High</td>
                <td>{high_severity}</td>
                <td>Critical issues that require immediate attention</td>
            </tr>
            <tr class="medium">
                <td>Medium</td>
                <td>{medium_severity}</td>
                <td>Important issues that should be addressed soon</td>
            </tr>
            <tr class="low">
                <td>Low</td>
                <td>{low_severity}</td>
                <td>Minor issues that should be reviewed</td>
            </tr>
        </table>
    </div>
    
    <div class="summary-box">
        <h2>Key Findings</h2>
        <ul>
""")
            
            for finding in key_findings:
                f.write(f"            <li>{finding}</li>\n")
            
            if not key_findings:
                f.write("            <li>No significant issues found</li>\n")
            
            f.write("""        </ul>
    </div>
""")
            
            if top_recommendations:
                f.write("""    <div class="summary-box">
        <h2>Top Recommendations</h2>
        <table>
            <tr>
                <th>Recommendation</th>
                <th>Severity</th>
                <th>Target</th>
            </tr>
""")
                
                for rec in top_recommendations:
                    severity_class = rec.get('severity', 'low').lower()
                    f.write(f"""            <tr class="{severity_class}">
                <td>{rec.get('recommendation', 'Unknown')}</td>
                <td>{rec.get('severity', 'Unknown').upper()}</td>
                <td>{rec.get('target', 'Unknown')}</td>
            </tr>
""")
                
                f.write("""        </table>
    </div>
""")
            
            f.write("""</body>
</html>""")
    
    def _get_remediation_step(self, result):
        """Get remediation step for a failed check"""
        # First check if the result has a remediation field
        if 'remediation' in result:
            return result['remediation']
        
        # If not, check if there's a recommendation in the assessment results
        for rec in self.assessment_results.get('recommendations', []):
            if (rec.get('setting') == result.get('setting_name') and
                rec.get('target', '').endswith(result.get('target', ''))):
                return rec.get('recommendation', '')
        
        # If no specific remediation is found, generate a generic one
        setting_name = result.get('setting_name', 'Unknown')
        baseline_value = result.get('baseline_value', 'Unknown')
        return f"Configure {setting_name} to match the baseline value: {baseline_value}. This can typically be done through Group Policy or local security policy."
    
    def generate_report_preview(self, report_type='technical', format='html'):
        """
        Generate a preview of a report.
        
        Args:
            report_type: Type of report to preview ('technical' or 'executive')
            format: Format of the preview ('html' or 'json')
            
        Returns:
            Preview content as HTML or JSON
        """
        logger.info(f"Generating {report_type} report preview in {format} format")
        
        if format == 'html':
            # Create a temporary file for the preview
            preview_path = os.path.join(self.output_dir, f"preview_{report_type}_{self.timestamp}.html")
            
            if report_type == 'executive':
                self._generate_executive_html(preview_path)
            else:
                self._generate_technical_html(preview_path)
            
            # Read the generated HTML
            with open(preview_path, 'r') as f:
                preview_content = f.read()
            
            return preview_content
        else:
            # Generate JSON preview
            if report_type == 'executive':
                return self._generate_executive_json_preview()
            else:
                return self._generate_technical_json_preview()
    
    def _generate_technical_json_preview(self):
        """Generate technical report preview in JSON format"""
        # Count failed checks
        failed_checks = []
        
        # Function to collect failed checks
        def collect_failed_checks(results, target):
            for result in results:
                if result.get('status') == 'fail':
                    failed_checks.append({
                        'target': target,
                        'setting_name': result.get('setting_name', 'Unknown'),
                        'setting_path': result.get('setting_path', ''),
                        'baseline_value': result.get('baseline_value', 'Unknown'),
                        'actual_value': result.get('actual_value', 'Unknown'),
                        'severity': result.get('severity', 'Unknown'),
                        'remediation': self._get_remediation_step(result)
                    })
        
        # Collect failed checks from domain controllers
        for dc in self.assessment_results.get('domain_controllers', []):
            dc_name = dc.get('name', 'Unknown')
            collect_failed_checks(dc.get('results', []), f"DC: {dc_name}")
        
        # Collect failed checks from computers
        for computer in self.assessment_results.get('computers', []):
            computer_name = computer.get('name', 'Unknown')
            collect_failed_checks(computer.get('results', []), f"Computer: {computer_name}")
        
        # Collect failed checks from domain policies
        if 'password_policy' in self.assessment_results.get('domain_policies', {}):
            collect_failed_checks(
                self.assessment_results['domain_policies']['password_policy'].get('results', []),
                "Domain Password Policy"
            )
        
        # Sort failed checks by severity
        failed_checks.sort(
            key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x.get('severity', 'low'), 3)
        )
        
        # Generate JSON preview
        summary = self.assessment_results.get('summary', {})
        
        return {
            'title': 'Technical Security Assessment Report',
            'domain': self.domain,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_checks': summary.get('total_checks', 0),
                'passed': summary.get('passed', 0),
                'failed': summary.get('failed', 0),
                'warning': summary.get('warning', 0),
                'not_applicable': summary.get('not_applicable', 0),
                'compliance_percentage': summary.get('compliance_percentage', 0)
            },
            'failed_checks': failed_checks
        }
    
    def _generate_executive_json_preview(self):
        """Generate executive report preview in JSON format"""
        # Count severity issues
        high_severity = 0
        medium_severity = 0
        low_severity = 0
        
        # Function to count severity issues
        def count_severity(results):
            nonlocal high_severity, medium_severity, low_severity
            for result in results:
                if result.get('status') == 'fail':
                    severity = result.get('severity', '').lower()
                    if severity == 'high':
                        high_severity += 1
                    elif severity == 'medium':
                        medium_severity += 1
                    elif severity == 'low':
                        low_severity += 1
        
        # Count issues from domain controllers
        for dc in self.assessment_results.get('domain_controllers', []):
            count_severity(dc.get('results', []))
        
        # Count issues from computers
        for computer in self.assessment_results.get('computers', []):
            count_severity(computer.get('results', []))
        
        # Count issues from domain policies
        if 'password_policy' in self.assessment_results.get('domain_policies', {}):
            count_severity(self.assessment_results['domain_policies']['password_policy'].get('results', []))
        
        # Generate key findings
        key_findings = []
        
        summary = self.assessment_results.get('summary', {})
        compliance = summary.get('compliance_percentage', 0)
        
        if high_severity > 0:
            key_findings.append(f"{high_severity} high severity issues require immediate attention")
        
        if compliance < 70:
            key_findings.append(f"Overall compliance is below recommended threshold (70%)")
        
        if 'password_policy' in self.assessment_results.get('domain_policies', {}):
            password_policy = self.assessment_results['domain_policies']['password_policy']
            failed_password_policies = [r for r in password_policy.get('results', []) if r.get('status') == 'fail']
            
            if failed_password_policies:
                key_findings.append("Domain password policy does not meet security requirements")
        
        # Get top recommendations
        top_recommendations = []
        if self.assessment_results.get('recommendations'):
            # Sort recommendations by severity
            sorted_recommendations = sorted(
                self.assessment_results.get('recommendations', []),
                key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x.get('severity', 'low'), 3)
            )
            
            # Get top 5 recommendations
            top_recommendations = sorted_recommendations[:5]
        
        # Generate JSON preview
        return {
            'title': 'Executive Security Assessment Summary',
            'domain': self.domain,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'organization': self.report_config.get('company_name', 'Your Organization'),
            'compliance': compliance,
            'summary': {
                'total_checks': summary.get('total_checks', 0),
                'passed': summary.get('passed', 0),
                'failed': summary.get('failed', 0)
            },
            'severity_breakdown': {
                'high': high_severity,
                'medium': medium_severity,
                'low': low_severity
            },
            'key_findings': key_findings,
            'top_recommendations': [
                {
                    'recommendation': rec.get('recommendation', 'Unknown'),
                    'severity': rec.get('severity', 'Unknown'),
                    'target': rec.get('target', 'Unknown')
                } for rec in top_recommendations
            ]
        }
