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
        
        logger.debug(f"Initialized report generator for domain: {self.domain}")
    
    def generate_csv(self):
        """
        Generate a CSV report of the assessment results.
        
        Returns:
            Path to the generated CSV file
        """
        logger.info("Generating CSV report")
        
        # Define CSV filename
        filename = f"ad_assessment_{self.domain}_{self.timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', newline='') as csvfile:
                # Create CSV writer
                csv_writer = csv.writer(csvfile)
                
                # Write header
                csv_writer.writerow([
                    'Target', 'Setting Name', 'Setting Path', 'Baseline Value',
                    'Actual Value', 'Status', 'Severity'
                ])
                
                # Write domain controller results
                for dc in self.assessment_results.get('domain_controllers', []):
                    dc_name = dc.get('name', 'Unknown')
                    for result in dc.get('results', []):
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
                        csv_writer.writerow([
                            "Domain Password Policy",
                            result.get('setting_name', 'Unknown'),
                            '',  # No path for domain policies
                            result.get('baseline_value', 'Unknown'),
                            result.get('actual_value', 'Unknown'),
                            result.get('status', 'Unknown'),
                            result.get('severity', 'Unknown')
                        ])
            
            logger.info(f"CSV report generated: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating CSV report: {str(e)}", exc_info=True)
            return ""
    
    def generate_pdf(self):
        """
        Generate a PDF report.
        
        Returns:
            Path to the generated PDF file
        """
        logger.info("Generating PDF report")
        
        # Define PDF filename
        filename = f"ad_assessment_{self.domain}_{self.timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # In a real implementation, this would use a PDF generation library
            # For now, we'll create a simple HTML file as a placeholder
            html_path = os.path.join(self.output_dir, f"ad_assessment_{self.domain}_{self.timestamp}.html")
            
            with open(html_path, 'w') as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Active Directory Security Assessment Report</title>
</head>
<body>
    <h1>Active Directory Security Assessment Report</h1>
    <p>Domain: {self.domain}</p>
    <p>Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>This is a placeholder for the PDF report.</p>
</body>
</html>""")
            
            logger.info(f"PDF report placeholder generated: {html_path}")
            return html_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}", exc_info=True)
            return ""
