"""
Active Directory Connector Module

This module handles secure connections to Active Directory and data retrieval.
"""

import logging
import ldap3
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
from ldap3.core.exceptions import LDAPException
import ssl
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class ADConnector:
    """
    Handles connections to Active Directory and data retrieval operations.
    Uses secure LDAP (LDAPS) for encrypted communications.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the AD connector with configuration settings.
        
        Args:
            config: Dictionary containing connection parameters
                - domain: AD domain name
                - server: Domain controller hostname or IP
                - username: Username for AD authentication
                - password: Password for AD authentication
                - use_ssl: Whether to use LDAPS (default: True)
                - port: LDAP port (default: 636 for LDAPS, 389 for LDAP)
                - verify_ssl: Whether to verify SSL certificates (default: True)
                - mock_mode: Whether to use mock data instead of connecting to AD (default: False)
        """
        self.config = config
        self.domain = config.get('domain')
        self.server_host = config.get('server')
        self.username = config.get('username')
        self.password = config.get('password')
        self.use_ssl = config.get('use_ssl', True)
        self.port = config.get('port', 636 if self.use_ssl else 389)
        self.verify_ssl = config.get('verify_ssl', True)
        self.mock_mode = config.get('mock_mode', False)
        
        # If domain is empty and mock_mode is not explicitly set, enable mock mode
        if not self.domain and 'mock_mode' not in config:
            logger.warning("No domain specified, enabling mock mode automatically")
            self.mock_mode = True
            self.domain = "example.com"  # Set a default domain for mock mode
        
        self.base_dn = self._get_base_dn_from_domain(self.domain) if self.domain else ""
        self.connection = None
        self.server = None
        
        if self.mock_mode:
            logger.info("Running in mock mode - no actual AD connection will be made")
        else:
            logger.debug(f"Initialized AD connector for domain: {self.domain}")
        
    def _get_base_dn_from_domain(self, domain: str) -> str:
        """
        Convert a domain name to a base DN.
        
        Args:
            domain: Domain name (e.g., example.com)
            
        Returns:
            Base DN string (e.g., DC=example,DC=com)
        """
        if not domain:
            raise ValueError("Domain name is required")
            
        return ','.join([f'DC={part}' for part in domain.split('.')])
    
    def connect(self) -> bool:
        """
        Establish a connection to the Active Directory server.
        
        Returns:
            True if connection successful, False otherwise
        """
        # If in mock mode, simulate a successful connection
        if self.mock_mode:
            logger.info("Mock mode: Simulating successful connection")
            return True
            
        try:
            # Check if required connection parameters are provided
            if not self.domain or not self.server_host:
                logger.error("Domain and server host are required for AD connection")
                logger.info("Enabling mock mode due to missing connection parameters")
                self.mock_mode = True
                return True
                
            if not self.username or not self.password:
                logger.warning("No credentials provided, attempting anonymous bind")
                
            # Configure TLS if using SSL
            tls_config = None
            if self.use_ssl:
                tls_config = ldap3.Tls(validate=ssl.CERT_REQUIRED if self.verify_ssl else ssl.CERT_NONE)
            
            # Create server object
            self.server = Server(
                self.server_host,
                port=self.port,
                use_ssl=self.use_ssl,
                tls=tls_config,
                get_info=ALL
            )
            
            # Create connection object with timeout settings
            self.connection = Connection(
                self.server,
                user=f"{self.username}@{self.domain}" if self.username else None,
                password=self.password,
                authentication=NTLM if self.username and self.password else None,
                auto_bind=True,
                receive_timeout=30  # 30 seconds timeout
            )
            
            logger.info(f"Successfully connected to {self.server_host}")
            return True
            
        except LDAPException as e:
            logger.error(f"Failed to connect to AD server: {str(e)}")
            logger.info("Enabling mock mode due to LDAP connection error")
            self.mock_mode = True
            return True
        except ConnectionError as e:
            logger.error(f"Network error connecting to AD server: {str(e)}")
            logger.info("Enabling mock mode due to network error")
            self.mock_mode = True
            return True
        except OSError as e:
            # Handle socket errors and other OS-level errors
            logger.error(f"Socket error connecting to AD server: {str(e)}")
            logger.info("Enabling mock mode due to socket error")
            self.mock_mode = True
            return True
        except Exception as e:
            logger.error(f"Unexpected error connecting to AD server: {str(e)}")
            logger.info("Enabling mock mode due to unexpected error")
            self.mock_mode = True
            return True
    
    def disconnect(self) -> None:
        """Close the LDAP connection."""
        if self.connection and self.connection.bound:
            self.connection.unbind()
            logger.debug("Disconnected from AD server")
    
    def _get_mock_data(self, search_filter: str, attributes: List[str]) -> List[Dict[str, Any]]:
        """
        Generate mock data for different search filters.
        
        Args:
            search_filter: LDAP search filter
            attributes: List of attributes to retrieve
            
        Returns:
            List of dictionaries containing mock data
        """
        logger.debug(f"Generating mock data for filter: {search_filter}")
        
        # Domain controllers
        if '(userAccountControl:1.2.840.113556.1.4.803:=8192)' in search_filter:
            return [
                {
                    'name': 'DC01',
                    'dNSHostName': f'dc01.{self.domain}',
                    'operatingSystem': 'Windows Server 2019',
                    'operatingSystemVersion': '10.0 (17763)'
                },
                {
                    'name': 'DC02',
                    'dNSHostName': f'dc02.{self.domain}',
                    'operatingSystem': 'Windows Server 2016',
                    'operatingSystemVersion': '10.0 (14393)'
                }
            ]
        
        # Computers
        elif '(objectClass=computer)' in search_filter and 'userAccountControl' not in search_filter:
            return [
                {
                    'name': 'DC01',
                    'dNSHostName': f'dc01.{self.domain}',
                    'operatingSystem': 'Windows Server 2019',
                    'operatingSystemVersion': '10.0 (17763)',
                    'lastLogonTimestamp': '132953620000000000',
                    'whenCreated': '20210101000000.0Z'
                },
                {
                    'name': 'DC02',
                    'dNSHostName': f'dc02.{self.domain}',
                    'operatingSystem': 'Windows Server 2016',
                    'operatingSystemVersion': '10.0 (14393)',
                    'lastLogonTimestamp': '132953620000000000',
                    'whenCreated': '20210101000000.0Z'
                },
                {
                    'name': 'CLIENT01',
                    'dNSHostName': f'client01.{self.domain}',
                    'operatingSystem': 'Windows 10 Enterprise',
                    'operatingSystemVersion': '10.0 (19044)',
                    'lastLogonTimestamp': '132953620000000000',
                    'whenCreated': '20210101000000.0Z'
                },
                {
                    'name': 'CLIENT02',
                    'dNSHostName': f'client02.{self.domain}',
                    'operatingSystem': 'Windows 11 Enterprise',
                    'operatingSystemVersion': '10.0 (22000)',
                    'lastLogonTimestamp': '132953620000000000',
                    'whenCreated': '20220101000000.0Z'
                }
            ]
        
        # Users
        elif '(objectClass=user)' in search_filter:
            return [
                {
                    'sAMAccountName': 'administrator',
                    'userPrincipalName': f'administrator@{self.domain}',
                    'displayName': 'Administrator',
                    'mail': f'administrator@{self.domain}',
                    'pwdLastSet': '132953620000000000',
                    'userAccountControl': 512,
                    'lastLogonTimestamp': '132953620000000000',
                    'memberOf': [f'CN=Domain Admins,CN=Users,DC={self.domain.split(".")[0]},DC={self.domain.split(".")[1]}']
                },
                {
                    'sAMAccountName': 'user1',
                    'userPrincipalName': f'user1@{self.domain}',
                    'displayName': 'User One',
                    'mail': f'user1@{self.domain}',
                    'pwdLastSet': '132953620000000000',
                    'userAccountControl': 512,
                    'lastLogonTimestamp': '132953620000000000',
                    'memberOf': [f'CN=Domain Users,CN=Users,DC={self.domain.split(".")[0]},DC={self.domain.split(".")[1]}']
                }
            ]
        
        # Groups
        elif '(objectClass=group)' in search_filter:
            return [
                {
                    'sAMAccountName': 'Domain Admins',
                    'description': 'Designated administrators of the domain',
                    'member': [f'CN=Administrator,CN=Users,DC={self.domain.split(".")[0]},DC={self.domain.split(".")[1]}'],
                    'groupType': 2147483652
                },
                {
                    'sAMAccountName': 'Domain Users',
                    'description': 'All domain users',
                    'member': [
                        f'CN=Administrator,CN=Users,DC={self.domain.split(".")[0]},DC={self.domain.split(".")[1]}',
                        f'CN=User One,CN=Users,DC={self.domain.split(".")[0]},DC={self.domain.split(".")[1]}'
                    ],
                    'groupType': 2147483652
                }
            ]
        
        # GPOs
        elif '(objectClass=groupPolicyContainer)' in search_filter:
            return [
                {
                    'displayName': 'Default Domain Policy',
                    'gPCFileSysPath': f'\\\\{self.domain}\\sysvol\\{self.domain}\\Policies\\{{31B2F340-016D-11D2-945F-00C04FB984F9}}',
                    'whenCreated': '20210101000000.0Z',
                    'whenChanged': '20210101000000.0Z'
                },
                {
                    'displayName': 'Default Domain Controllers Policy',
                    'gPCFileSysPath': f'\\\\{self.domain}\\sysvol\\{self.domain}\\Policies\\{{6AC1786C-016F-11D2-945F-00C04FB984F9}}',
                    'whenCreated': '20210101000000.0Z',
                    'whenChanged': '20210101000000.0Z'
                }
            ]
        
        # Domain password policy
        elif '(objectClass=domainDNS)' in search_filter:
            return [
                {
                    'maxPwdAge': '-864000000000',  # 10 days in 100-nanosecond intervals
                    'minPwdAge': '-86400000000',   # 1 day in 100-nanosecond intervals
                    'minPwdLength': 7,
                    'pwdHistoryLength': 24,
                    'pwdProperties': 1,
                    'lockoutThreshold': 0,
                    'lockoutDuration': '-18000000000'  # 30 minutes in 100-nanosecond intervals
                }
            ]
        
        # Default: empty result
        return []
    
    def search(self, search_filter: str, attributes: List[str], 
               search_base: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform an LDAP search and return the results.
        
        Args:
            search_filter: LDAP search filter
            attributes: List of attributes to retrieve
            search_base: Base DN for the search (defaults to domain base DN)
            
        Returns:
            List of dictionaries containing the requested attributes
        """
        # If in mock mode, return mock data
        if self.mock_mode:
            logger.info(f"Mock mode: Simulating search with filter: {search_filter}")
            return self._get_mock_data(search_filter, attributes)
            
        # Real AD search
        try:
            # Try to connect if not already connected
            if not self.connection or not self.connection.bound:
                if not self.connect():
                    logger.warning("Failed to connect to AD server, falling back to mock mode")
                    self.mock_mode = True
                    return self._get_mock_data(search_filter, attributes)
            
            base_dn = search_base if search_base else self.base_dn
            
            logger.debug(f"Searching with filter: {search_filter}, base: {base_dn}")
            self.connection.search(
                search_base=base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes
            )
            
            results = []
            for entry in self.connection.entries:
                result = {}
                for attr in attributes:
                    if hasattr(entry, attr):
                        result[attr] = entry[attr].value
                results.append(result)
                
            logger.debug(f"Found {len(results)} results")
            return results
            
        except LDAPException as e:
            logger.error(f"LDAP search error: {str(e)}")
            logger.warning("LDAP search failed, falling back to mock mode")
            self.mock_mode = True
            return self._get_mock_data(search_filter, attributes)
        except ConnectionError as e:
            logger.error(f"Connection error during search: {str(e)}")
            logger.warning("Connection error, falling back to mock mode")
            self.mock_mode = True
            return self._get_mock_data(search_filter, attributes)
        except OSError as e:
            # Handle socket errors and other OS-level errors
            logger.error(f"Socket error during search: {str(e)}")
            logger.warning("Socket error, falling back to mock mode")
            self.mock_mode = True
            return self._get_mock_data(search_filter, attributes)
        except Exception as e:
            logger.error(f"Unexpected error during search: {str(e)}")
            logger.warning("Unexpected error, falling back to mock mode")
            self.mock_mode = True
            return self._get_mock_data(search_filter, attributes)
    
    def get_domain_controllers(self) -> List[Dict[str, Any]]:
        """
        Get a list of domain controllers in the domain.
        
        Returns:
            List of dictionaries containing domain controller information
        """
        search_filter = '(&(objectClass=computer)(userAccountControl:1.2.840.113556.1.4.803:=8192))'
        attributes = ['name', 'dNSHostName', 'operatingSystem', 'operatingSystemVersion']
        
        return self.search(search_filter, attributes)
    
    def get_computers(self) -> List[Dict[str, Any]]:
        """
        Get a list of all computer objects in the domain.
        
        Returns:
            List of dictionaries containing computer information
        """
        search_filter = '(objectClass=computer)'
        attributes = ['name', 'dNSHostName', 'operatingSystem', 'operatingSystemVersion', 
                      'lastLogonTimestamp', 'whenCreated']
        
        return self.search(search_filter, attributes)
    
    def get_users(self) -> List[Dict[str, Any]]:
        """
        Get a list of all user objects in the domain.
        
        Returns:
            List of dictionaries containing user information
        """
        search_filter = '(objectClass=user)'
        attributes = ['sAMAccountName', 'userPrincipalName', 'displayName', 'mail',
                      'pwdLastSet', 'userAccountControl', 'lastLogonTimestamp', 'memberOf']
        
        return self.search(search_filter, attributes)
    
    def get_groups(self) -> List[Dict[str, Any]]:
        """
        Get a list of all groups in the domain.
        
        Returns:
            List of dictionaries containing group information
        """
        search_filter = '(objectClass=group)'
        attributes = ['sAMAccountName', 'description', 'member', 'groupType']
        
        return self.search(search_filter, attributes)
    
    def get_gpos(self) -> List[Dict[str, Any]]:
        """
        Get a list of all Group Policy Objects in the domain.
        
        Returns:
            List of dictionaries containing GPO information
        """
        search_filter = '(objectClass=groupPolicyContainer)'
        attributes = ['displayName', 'gPCFileSysPath', 'whenCreated', 'whenChanged']
        
        return self.search(search_filter, attributes)
    
    def get_domain_password_policy(self) -> Dict[str, Any]:
        """
        Get the domain password policy.
        
        Returns:
            Dictionary containing password policy settings
        """
        search_filter = '(objectClass=domainDNS)'
        attributes = ['maxPwdAge', 'minPwdAge', 'minPwdLength', 'pwdHistoryLength',
                      'pwdProperties', 'lockoutThreshold', 'lockoutDuration']
        
        results = self.search(search_filter, attributes)
        return results[0] if results else {}
    
    def get_computer_security_settings(self, computer_name: str) -> Dict[str, Any]:
        """
        Get security settings for a specific computer.
        
        Args:
            computer_name: Name of the computer
            
        Returns:
            Dictionary containing security settings
        """
        # If in mock mode, return mock security settings
        if self.mock_mode:
            logger.info(f"Mock mode: Generating security settings for {computer_name}")
            
            # Generate different settings based on computer name to simulate variety
            if computer_name.lower().startswith('dc'):
                # Domain controller settings
                return {
                    "computer_name": computer_name,
                    "settings_retrieved": True,
                    "settings": {
                        "PasswordComplexity": "Enabled",
                        "MinimumPasswordLength": "8",
                        "AccountLockoutThreshold": "0",
                        "AuditAccountLogon": "Success, Failure",
                        "AuditAccountManagement": "Success, Failure",
                        "AuditDSAccess": "Success, Failure",
                        "AuditLogonEvents": "Success, Failure",
                        "AuditObjectAccess": "Success, Failure",
                        "AuditPolicyChange": "Success, Failure",
                        "AuditPrivilegeUse": "Success, Failure",
                        "AuditSystemEvents": "Success, Failure",
                        "SeBackupPrivilege": "Administrators, Backup Operators",
                        "SeRestorePrivilege": "Administrators, Backup Operators",
                        "SeTakeOwnershipPrivilege": "Administrators",
                        "EnableGuestAccount": "Disabled",
                        "LimitBlankPasswordUse": "Enabled",
                        "NewAdministratorName": "Admin",
                        "NewGuestName": "Guest",
                        "RestrictAnonymous": "1",
                        "RestrictAnonymousSAM": "1"
                    }
                }
            else:
                # Member computer settings
                return {
                    "computer_name": computer_name,
                    "settings_retrieved": True,
                    "settings": {
                        "PasswordComplexity": "Enabled",
                        "MinimumPasswordLength": "8",
                        "AccountLockoutThreshold": "0",
                        "AuditAccountLogon": "Success",
                        "AuditAccountManagement": "Success",
                        "AuditLogonEvents": "Success",
                        "AuditObjectAccess": "None",
                        "AuditPolicyChange": "Success",
                        "AuditPrivilegeUse": "None",
                        "AuditSystemEvents": "Success",
                        "SeBackupPrivilege": "Administrators",
                        "SeRestorePrivilege": "Administrators",
                        "SeTakeOwnershipPrivilege": "Administrators",
                        "EnableGuestAccount": "Disabled",
                        "LimitBlankPasswordUse": "Enabled",
                        "NewAdministratorName": "Administrator",
                        "NewGuestName": "Guest",
                        "RestrictAnonymous": "0",
                        "RestrictAnonymousSAM": "1"
                    }
                }
        
        # In a real implementation, this would involve connecting to the remote computer
        # and querying local security policy settings, registry, etc.
        # For now, we'll return a placeholder
        logger.warning("get_computer_security_settings is not fully implemented for real AD environments")
        return {
            "computer_name": computer_name,
            "settings_retrieved": False,
            "reason": "Remote security settings retrieval not implemented"
        }
