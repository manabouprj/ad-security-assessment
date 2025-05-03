"""
Tests for the Report Generator module.
"""

import pytest
import os
from unittest.mock import Mock, patch
from src.reports.report_generator import ReportGenerator

@pytest.fixture
def sample_results():
    return {
        'domain_controllers': [
            {'name': 'DC1', 'dNSHostName': 'dc1.test.local'},
            {'name': 'DC2', 'dNSHostName': 'dc2.test.local'}
        ],
        'computers': [
            {'name': 'PC1', 'operatingSystem': 'Windows 10'},
            {'name': 'PC2', 'operatingSystem': 'Windows Server 2019'}
        ],
        'domain_policies': [
            {'cn': 'Default Domain Policy'},
            {'cn': 'Default Domain Controllers Policy'}
        ],
        'password_policy': {
            'findings': ['Weak password length requirement'],
            'recommendations': ['Increase minimum password length']
        },
        'account_lockout': {
            'findings': ['No account lockout policy'],
            'recommendations': ['Enable account lockout']
        },
        'audit_policy': {
            'findings': ['Insufficient audit logging'],
            'recommendations': ['Enable comprehensive auditing']
        }
    }

@pytest.fixture
def report_generator(sample_results):
    return ReportGenerator(sample_results)

def test_init(report_generator, sample_results):
    """Test ReportGenerator initialization."""
    assert report_generator.results == sample_results
    assert hasattr(report_generator, 'output_dir')

def test_generate_pdf(report_generator, tmp_path):
    """Test PDF report generation."""
    report_generator.output_dir = str(tmp_path)
    pdf_path = report_generator.generate_pdf()
    
    assert os.path.exists(pdf_path)
    assert pdf_path.endswith('.pdf')
    assert os.path.getsize(pdf_path) > 0

def test_generate_csv(report_generator, tmp_path):
    """Test CSV report generation."""
    report_generator.output_dir = str(tmp_path)
    csv_path = report_generator.generate_csv()
    
    assert os.path.exists(csv_path)
    assert csv_path.endswith('.csv')
    assert os.path.getsize(csv_path) > 0

def test_generate_summary(report_generator):
    """Test summary generation."""
    summary = report_generator.generate_summary()
    
    assert isinstance(summary, dict)
    assert 'total_findings' in summary
    assert 'risk_levels' in summary
    assert 'categories' in summary

def test_generate_executive_summary(report_generator):
    """Test executive summary generation."""
    summary = report_generator.generate_executive_summary()
    
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert 'findings' in summary.lower()
    assert 'recommendations' in summary.lower()

def test_format_findings(report_generator):
    """Test findings formatting."""
    findings = report_generator.format_findings()
    
    assert isinstance(findings, list)
    assert len(findings) > 0
    for finding in findings:
        assert 'category' in finding
        assert 'description' in finding
        assert 'recommendation' in finding

def test_generate_charts(report_generator, tmp_path):
    """Test chart generation."""
    report_generator.output_dir = str(tmp_path)
    charts = report_generator.generate_charts()
    
    assert isinstance(charts, dict)
    assert 'findings_by_category' in charts
    assert 'risk_distribution' in charts
    for chart_path in charts.values():
        assert os.path.exists(chart_path)
        assert os.path.getsize(chart_path) > 0

def test_invalid_results():
    """Test handling of invalid results."""
    with pytest.raises(ValueError):
        ReportGenerator(None)
    
    with pytest.raises(ValueError):
        ReportGenerator({})  # Empty results

def test_custom_output_dir(sample_results, tmp_path):
    """Test custom output directory."""
    custom_dir = str(tmp_path / "custom_reports")
    generator = ReportGenerator(sample_results, output_dir=custom_dir)
    
    assert generator.output_dir == custom_dir
    assert os.path.exists(custom_dir)

def test_report_metadata(report_generator):
    """Test report metadata generation."""
    metadata = report_generator.generate_metadata()
    
    assert isinstance(metadata, dict)
    assert 'timestamp' in metadata
    assert 'version' in metadata
    assert 'environment' in metadata 