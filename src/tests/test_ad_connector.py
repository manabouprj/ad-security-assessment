"""
Tests for the AD Connector module.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.ad_connector import ADConnector

@pytest.fixture
def mock_ldap():
    with patch('ldap3.Server') as mock_server, \
         patch('ldap3.Connection') as mock_connection:
        mock_conn = Mock()
        mock_connection.return_value = mock_conn
        mock_conn.bind.return_value = True
        yield mock_conn

@pytest.fixture
def ad_connector():
    return ADConnector(
        domain="test.local",
        username="test_user",
        password="test_pass"
    )

def test_init(ad_connector):
    """Test ADConnector initialization."""
    assert ad_connector.domain == "test.local"
    assert ad_connector.username == "test_user"
    assert ad_connector.password == "test_pass"

def test_connect_success(ad_connector, mock_ldap):
    """Test successful AD connection."""
    result = ad_connector.connect()
    assert result['success'] is True
    assert 'connection' in result

def test_connect_failure(ad_connector, mock_ldap):
    """Test failed AD connection."""
    mock_ldap.bind.return_value = False
    result = ad_connector.connect()
    assert result['success'] is False
    assert 'error' in result

def test_get_domain_controllers(ad_connector, mock_ldap):
    """Test getting domain controllers."""
    mock_ldap.entries = [
        {'name': 'DC1', 'dNSHostName': 'dc1.test.local'},
        {'name': 'DC2', 'dNSHostName': 'dc2.test.local'}
    ]
    mock_ldap.search.return_value = True
    
    controllers = ad_connector.get_domain_controllers()
    assert len(controllers) == 2
    assert controllers[0]['name'] == 'DC1'
    assert controllers[1]['dNSHostName'] == 'dc2.test.local'

def test_get_computers(ad_connector, mock_ldap):
    """Test getting computers."""
    mock_ldap.entries = [
        {'name': 'PC1', 'operatingSystem': 'Windows 10'},
        {'name': 'PC2', 'operatingSystem': 'Windows Server 2019'}
    ]
    mock_ldap.search.return_value = True
    
    computers = ad_connector.get_computers()
    assert len(computers) == 2
    assert computers[0]['name'] == 'PC1'
    assert computers[1]['operatingSystem'] == 'Windows Server 2019'

def test_get_domain_policies(ad_connector, mock_ldap):
    """Test getting domain policies."""
    mock_ldap.entries = [
        {'cn': 'Default Domain Policy', 'distinguishedName': 'CN=Default Domain Policy,CN=Policies,CN=System,DC=test,DC=local'},
        {'cn': 'Default Domain Controllers Policy', 'distinguishedName': 'CN=Default Domain Controllers Policy,CN=Policies,CN=System,DC=test,DC=local'}
    ]
    mock_ldap.search.return_value = True
    
    policies = ad_connector.get_domain_policies()
    assert len(policies) == 2
    assert policies[0]['cn'] == 'Default Domain Policy'
    assert 'Default Domain Controllers Policy' in policies[1]['distinguishedName']

def test_test_connection(ad_connector, mock_ldap):
    """Test connection testing."""
    result = ad_connector.test_connection()
    assert result['success'] is True
    assert 'details' in result

def test_test_authentication(ad_connector, mock_ldap):
    """Test authentication testing."""
    result = ad_connector.test_authentication()
    assert result['success'] is True
    assert 'details' in result 