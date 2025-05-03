"""
Tests for the Security Assessment module.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.security_assessment import SecurityAssessment

@pytest.fixture
def mock_ad_connector():
    connector = Mock()
    connector.get_domain_controllers.return_value = [
        {'name': 'DC1', 'dNSHostName': 'dc1.test.local'},
        {'name': 'DC2', 'dNSHostName': 'dc2.test.local'}
    ]
    connector.get_computers.return_value = [
        {'name': 'PC1', 'operatingSystem': 'Windows 10'},
        {'name': 'PC2', 'operatingSystem': 'Windows Server 2019'}
    ]
    connector.get_domain_policies.return_value = [
        {'cn': 'Default Domain Policy'},
        {'cn': 'Default Domain Controllers Policy'}
    ]
    return connector

@pytest.fixture
def security_assessment(mock_ad_connector):
    with patch('src.core.security_assessment.ADConnector') as mock_connector_class:
        mock_connector_class.return_value = mock_ad_connector
        assessment = SecurityAssessment()
        return assessment

def test_init(security_assessment):
    """Test SecurityAssessment initialization."""
    assert security_assessment is not None
    assert hasattr(security_assessment, 'ad_connector')

def test_run_assessment(security_assessment, mock_ad_connector):
    """Test running a security assessment."""
    results = security_assessment.run()
    assert results is not None
    assert 'domain_controllers' in results
    assert 'computers' in results
    assert 'domain_policies' in results
    assert len(results['domain_controllers']) == 2
    assert len(results['computers']) == 2
    assert len(results['domain_policies']) == 2

def test_assess_password_policy(security_assessment):
    """Test password policy assessment."""
    mock_policy = {
        'minPwdLength': ['12'],
        'pwdHistoryLength': ['24'],
        'maxPwdAge': ['42'],
        'minPwdAge': ['1'],
        'lockoutThreshold': ['5'],
        'lockoutDuration': ['30']
    }
    
    results = security_assessment.assess_password_policy(mock_policy)
    assert results is not None
    assert 'findings' in results
    assert 'recommendations' in results

def test_assess_account_lockout(security_assessment):
    """Test account lockout assessment."""
    mock_policy = {
        'lockoutThreshold': ['5'],
        'lockoutDuration': ['30'],
        'lockoutObservationWindow': ['30']
    }
    
    results = security_assessment.assess_account_lockout(mock_policy)
    assert results is not None
    assert 'findings' in results
    assert 'recommendations' in results

def test_assess_audit_policy(security_assessment):
    """Test audit policy assessment."""
    mock_policy = {
        'auditLogonEvents': ['3'],
        'auditObjectAccess': ['3'],
        'auditPrivilegeUse': ['3'],
        'auditPolicyChange': ['3'],
        'auditAccountManage': ['3'],
        'auditDSAccess': ['3']
    }
    
    results = security_assessment.assess_audit_policy(mock_policy)
    assert results is not None
    assert 'findings' in results
    assert 'recommendations' in results

def test_assess_system_access(security_assessment):
    """Test system access assessment."""
    mock_policy = {
        'enableGuestAccount': ['0'],
        'limitBlankPasswordUse': ['1'],
        'forceLogoffWhenHourExpire': ['1'],
        'newAdministratorName': ['Admin'],
        'newGuestName': ['Guest']
    }
    
    results = security_assessment.assess_system_access(mock_policy)
    assert results is not None
    assert 'findings' in results
    assert 'recommendations' in results

def test_assess_security_options(security_assessment):
    """Test security options assessment."""
    mock_policy = {
        'enableSecuritySignature': ['1'],
        'requireSecuritySignature': ['1'],
        'disablePasswordChange': ['0'],
        'clearTextPassword': ['0'],
        'enableForcedLogoff': ['1']
    }
    
    results = security_assessment.assess_security_options(mock_policy)
    assert results is not None
    assert 'findings' in results
    assert 'recommendations' in results

def test_generate_report(security_assessment):
    """Test report generation."""
    mock_results = {
        'domain_controllers': [{'name': 'DC1'}],
        'computers': [{'name': 'PC1'}],
        'domain_policies': [{'cn': 'Default Domain Policy'}],
        'password_policy': {'findings': [], 'recommendations': []},
        'account_lockout': {'findings': [], 'recommendations': []},
        'audit_policy': {'findings': [], 'recommendations': []},
        'system_access': {'findings': [], 'recommendations': []},
        'security_options': {'findings': [], 'recommendations': []}
    }
    
    report = security_assessment.generate_report(mock_results)
    assert report is not None
    assert 'summary' in report
    assert 'details' in report
    assert 'recommendations' in report 