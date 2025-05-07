"""
Report generation modules for CSV and PDF output.
"""

import os
from datetime import datetime
from .report_generator import ReportGenerator as BaseReportGenerator

class ReportGenerator:
    """
    Wrapper for the ReportGenerator class that provides compatibility with the API server.
    """
    
    def __init__(self, assessment_results):
        """
        Initialize the report generator with just assessment results.
        
        Args:
            assessment_results: Dictionary containing assessment results
        """
        # Create a temporary output directory for reports
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                 'reports', 
                                 f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize the base report generator
        self.base_generator = BaseReportGenerator(assessment_results, output_dir)
    
    def generate_pdf(self):
        """
        Generate a PDF report.
        
        Returns:
            Path to the generated PDF file
        """
        # The base generator returns a tuple of (executive_pdf, technical_pdf)
        # We'll return the technical report for now
        executive_pdf, technical_pdf = self.base_generator.generate_pdf_report()
        return technical_pdf
    
    def generate_csv(self):
        """
        Generate a CSV report.
        
        Returns:
            Path to the generated CSV file
        """
        return self.base_generator.generate_csv_report()
