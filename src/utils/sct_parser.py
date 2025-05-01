"""
Microsoft Security Configuration Toolkit (SCT) Parser

This module parses Microsoft Security Configuration Toolkit baselines
and provides them in a format that can be used for security assessments.
"""

import logging
import os
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SCTParser:
    """
    Parses Microsoft Security Configuration Toolkit baselines.
    """
    
    def __init__(self, baselines_path: str):
        """
        Initialize the SCT parser.
        
        Args:
            baselines_path: Path to the directory containing baseline files
        """
        self.baselines_path = baselines_path
        self.baselines = {}
        self.os_mapping = {
            'windows server 2022': 'WindowsServer2022',
            'windows server 2019': 'WindowsServer2019',
            'windows server 2016': 'WindowsServer2016',
            'windows server 2012 r2': 'WindowsServer2012R2',
            'windows 11': 'Windows11',
            'windows 10': 'Windows10',
            'windows 8.1': 'Windows81'
        }
        
        # Create baselines directory if it doesn't exist
        os.makedirs(baselines_path, exist_ok=True)
        
        # Load baselines
        self._load_baselines()
        
        logger.debug(f"Initialized SCT parser with baselines path: {baselines_path}")
    
    def _load_baselines(self) -> None:
        """Load all available baselines from the baselines directory."""
        if not os.path.exists(self.baselines_path):
            logger.warning(f"Baselines path does not exist: {self.baselines_path}")
            return
        
        try:
            # In a real implementation, this would parse actual SCT baseline files
            # For now, we'll create placeholder baselines
            self._create_placeholder_baselines()
            
            logger.info(f"Loaded {len(self.baselines)} baselines")
            
        except Exception as e:
            logger.error(f"Error loading baselines: {str(e)}", exc_info=True)
    
    def _create_placeholder_baselines(self) -> None:
        """Create placeholder baselines for demonstration purposes."""
        # Windows Server 2022 baseline
        self.baselines['WindowsServer2022'] = {
            'name': 'Windows Server 2022 Security Baseline',
            'version': '1.0',
            'settings': {
                'PasswordComplexity': {
                    'value': 'Enabled',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Password Policy',
                    'severity': 'high'
                },
                'MinimumPasswordLength': {
                    'value': '14',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Password Policy',
                    'severity': 'high'
                },
                'AccountLockoutThreshold': {
                    'value': '5',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Account Lockout Policy',
                    'severity': 'high'
                },
                'EnableFirewall': {
                    'value': 'Enabled',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Windows Firewall with Advanced Security',
                    'severity': 'high'
                }
            }
        }
        
        # Windows Server 2019 baseline
        self.baselines['WindowsServer2019'] = {
            'name': 'Windows Server 2019 Security Baseline',
            'version': '1.0',
            'settings': {
                'PasswordComplexity': {
                    'value': 'Enabled',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Password Policy',
                    'severity': 'high'
                },
                'MinimumPasswordLength': {
                    'value': '14',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Password Policy',
                    'severity': 'high'
                },
                'AccountLockoutThreshold': {
                    'value': '5',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Account Lockout Policy',
                    'severity': 'high'
                },
                'EnableFirewall': {
                    'value': 'Enabled',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Windows Firewall with Advanced Security',
                    'severity': 'high'
                }
            }
        }
        
        # Windows 10 baseline
        self.baselines['Windows10'] = {
            'name': 'Windows 10 Security Baseline',
            'version': '1.0',
            'settings': {
                'PasswordComplexity': {
                    'value': 'Enabled',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Password Policy',
                    'severity': 'high'
                },
                'MinimumPasswordLength': {
                    'value': '12',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Password Policy',
                    'severity': 'high'
                },
                'AccountLockoutThreshold': {
                    'value': '5',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Account Lockout Policy',
                    'severity': 'high'
                },
                'EnableFirewall': {
                    'value': 'Enabled',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Windows Firewall with Advanced Security',
                    'severity': 'high'
                }
            }
        }
        
        # Domain Password Policy baseline
        self.baselines['DomainPasswordPolicy'] = {
            'name': 'Domain Password Policy Baseline',
            'version': '1.0',
            'settings': {
                'MinimumPasswordLength': {
                    'value': '14',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Password Policy',
                    'severity': 'high'
                },
                'PasswordComplexity': {
                    'value': 'Enabled',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Password Policy',
                    'severity': 'high'
                },
                'PasswordHistorySize': {
                    'value': '24',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Password Policy',
                    'severity': 'medium'
                },
                'MaximumPasswordAge': {
                    'value': '60',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Password Policy',
                    'severity': 'medium'
                },
                'MinimumPasswordAge': {
                    'value': '1',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Password Policy',
                    'severity': 'medium'
                },
                'AccountLockoutThreshold': {
                    'value': '5',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Account Lockout Policy',
                    'severity': 'high'
                },
                'AccountLockoutDuration': {
                    'value': '15',
                    'path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Account Lockout Policy',
                    'severity': 'medium'
                }
            }
        }
    
    def get_baseline_for_os(self, os_name: str, os_version: str) -> Optional[Dict[str, Any]]:
        """
        Get the appropriate baseline for a given OS.
        
        Args:
            os_name: Operating system name (e.g., 'Windows Server')
            os_version: Operating system version (e.g., '2019')
            
        Returns:
            Baseline dictionary or None if no suitable baseline is found
        """
        if not os_name:
            logger.warning("No OS name provided")
            return None
        
        # Normalize OS name and version
        os_name = os_name.lower()
        os_version = os_version.lower() if os_version else ''
        
        # Try to find an exact match
        full_os = f"{os_name} {os_version}".strip()
        baseline_key = self.os_mapping.get(full_os)
        
        if baseline_key and baseline_key in self.baselines:
            logger.debug(f"Found exact baseline match for {full_os}: {baseline_key}")
            return self.baselines[baseline_key]
        
        # Try to match just the OS name
        for mapping_key, baseline_key in self.os_mapping.items():
            if os_name in mapping_key and baseline_key in self.baselines:
                logger.debug(f"Found partial baseline match for {os_name}: {baseline_key}")
                return self.baselines[baseline_key]
        
        # Default to Windows Server 2019 if it's a server OS
        if 'server' in os_name and 'WindowsServer2019' in self.baselines:
            logger.debug(f"Using default Windows Server 2019 baseline for {os_name} {os_version}")
            return self.baselines['WindowsServer2019']
        
        # Default to Windows 10 for client OS
        if 'WindowsServer2019' in self.baselines:
            logger.debug(f"Using default Windows 10 baseline for {os_name} {os_version}")
            return self.baselines['Windows10']
        
        logger.warning(f"No suitable baseline found for {os_name} {os_version}")
        return None
    
    def get_domain_password_policy_baseline(self) -> Optional[Dict[str, Any]]:
        """
        Get the baseline for domain password policy.
        
        Returns:
            Domain password policy baseline or None if not found
        """
        if 'DomainPasswordPolicy' in self.baselines:
            return self.baselines['DomainPasswordPolicy']
        
        logger.warning("Domain password policy baseline not found")
        return None
    
    def parse_baseline_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse a baseline file (XML or JSON).
        
        Args:
            file_path: Path to the baseline file
            
        Returns:
            Parsed baseline or None if parsing fails
        """
        if not os.path.exists(file_path):
            logger.warning(f"Baseline file does not exist: {file_path}")
            return None
        
        try:
            # Determine file type based on extension
            _, ext = os.path.splitext(file_path)
            
            if ext.lower() == '.json':
                # Parse JSON file
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif ext.lower() in ['.xml', '.admx']:
                # Parse XML file
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # In a real implementation, this would parse the XML structure
                # For now, return a placeholder
                return {
                    'name': os.path.basename(file_path),
                    'settings': {}
                }
            else:
                logger.warning(f"Unsupported file type: {ext}")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing baseline file {file_path}: {str(e)}", exc_info=True)
            return None
    
    def save_baseline(self, baseline_key: str, baseline: Dict[str, Any]) -> bool:
        """
        Save a baseline to the baselines directory.
        
        Args:
            baseline_key: Key for the baseline (e.g., 'WindowsServer2019')
            baseline: Baseline dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = os.path.join(self.baselines_path, f"{baseline_key}.json")
            
            with open(file_path, 'w') as f:
                json.dump(baseline, f, indent=2)
            
            # Update in-memory baseline
            self.baselines[baseline_key] = baseline
            
            logger.info(f"Saved baseline to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving baseline {baseline_key}: {str(e)}", exc_info=True)
            return False
