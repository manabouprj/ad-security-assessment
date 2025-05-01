"""
Operating System Detector

This module provides utilities for detecting and identifying operating systems.
"""

import logging
import re
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class OSDetector:
    """
    Detects and identifies operating systems based on name and version strings.
    """
    
    def __init__(self):
        """Initialize the OS detector."""
        # Define OS name patterns
        self.os_patterns = {
            'windows_server': re.compile(r'windows\s+server', re.IGNORECASE),
            'windows_client': re.compile(r'windows\s+(?!server)([\w\s]+)', re.IGNORECASE),
            'linux': re.compile(r'linux', re.IGNORECASE),
            'macos': re.compile(r'mac\s*os|darwin', re.IGNORECASE)
        }
        
        # Define version patterns
        self.version_patterns = {
            'windows_server': re.compile(r'(\d{4}(?:\s*r\d)?)', re.IGNORECASE),  # 2019, 2016, 2012 R2
            'windows_client': re.compile(r'((?:\d+\.)*\d+|xp|vista|[\w\s]+)', re.IGNORECASE),  # 10, 8.1, 7, XP
            'linux': re.compile(r'(\d+(?:\.\d+)*)', re.IGNORECASE),
            'macos': re.compile(r'(\d+(?:\.\d+)*)', re.IGNORECASE)
        }
        
        logger.debug("Initialized OS detector")
    
    def detect_os_type(self, os_string: str) -> Tuple[str, Optional[str]]:
        """
        Detect the OS type and version from a string.
        
        Args:
            os_string: String containing OS information
            
        Returns:
            Tuple of (os_type, os_version) where os_type is one of:
            'windows_server', 'windows_client', 'linux', 'macos', 'unknown'
        """
        if not os_string:
            return 'unknown', None
        
        # Check each OS pattern
        for os_type, pattern in self.os_patterns.items():
            if pattern.search(os_string):
                # Extract version if available
                version_match = self.version_patterns.get(os_type, re.compile(r'(\d+(?:\.\d+)*)')).search(os_string)
                version = version_match.group(1) if version_match else None
                
                logger.debug(f"Detected OS: {os_type}, version: {version}")
                return os_type, version
        
        # If no match, try to extract any version-like string
        version_match = re.search(r'(\d+(?:\.\d+)*)', os_string)
        version = version_match.group(1) if version_match else None
        
        logger.debug(f"Unknown OS type from string: {os_string}, possible version: {version}")
        return 'unknown', version
    
    def normalize_os_info(self, os_name: str, os_version: str = None) -> Dict[str, str]:
        """
        Normalize OS name and version information.
        
        Args:
            os_name: Operating system name
            os_version: Operating system version (optional)
            
        Returns:
            Dictionary with normalized OS information:
            {
                'type': OS type (windows_server, windows_client, linux, macos, unknown),
                'name': Normalized OS name,
                'version': Normalized version,
                'full_name': Full normalized OS name with version
            }
        """
        if not os_name:
            return {
                'type': 'unknown',
                'name': 'Unknown',
                'version': os_version or 'Unknown',
                'full_name': 'Unknown'
            }
        
        # Detect OS type and version
        os_type, detected_version = self.detect_os_type(os_name)
        
        # Use provided version if available, otherwise use detected version
        version = os_version or detected_version or 'Unknown'
        
        # Normalize OS name based on type
        if os_type == 'windows_server':
            name = 'Windows Server'
            full_name = f"Windows Server {version}"
        elif os_type == 'windows_client':
            name = 'Windows'
            full_name = f"Windows {version}"
        elif os_type == 'linux':
            name = 'Linux'
            full_name = f"Linux {version}"
        elif os_type == 'macos':
            name = 'macOS'
            full_name = f"macOS {version}"
        else:
            name = os_name
            full_name = f"{os_name} {version}" if version and version != 'Unknown' else os_name
        
        return {
            'type': os_type,
            'name': name,
            'version': version,
            'full_name': full_name
        }
    
    def is_server_os(self, os_info: str) -> bool:
        """
        Determine if the OS is a server operating system.
        
        Args:
            os_info: OS information string
            
        Returns:
            True if server OS, False otherwise
        """
        os_type, _ = self.detect_os_type(os_info)
        return os_type == 'windows_server' or ('linux' in os_info.lower() and 'server' in os_info.lower())
    
    def get_os_family(self, os_info: str) -> str:
        """
        Get the OS family (Windows, Linux, macOS).
        
        Args:
            os_info: OS information string
            
        Returns:
            OS family name
        """
        os_type, _ = self.detect_os_type(os_info)
        
        if os_type in ['windows_server', 'windows_client']:
            return 'Windows'
        elif os_type == 'linux':
            return 'Linux'
        elif os_type == 'macos':
            return 'macOS'
        else:
            return 'Unknown'
    
    def parse_windows_version(self, version_string: str) -> Dict[str, str]:
        """
        Parse Windows version information.
        
        Args:
            version_string: Windows version string (e.g., '10.0.19042')
            
        Returns:
            Dictionary with parsed version information
        """
        if not version_string:
            return {'major': 'Unknown', 'minor': 'Unknown', 'build': 'Unknown'}
        
        # Try to parse version string
        parts = version_string.split('.')
        
        result = {
            'major': parts[0] if len(parts) > 0 else 'Unknown',
            'minor': parts[1] if len(parts) > 1 else 'Unknown',
            'build': parts[2] if len(parts) > 2 else 'Unknown'
        }
        
        # Map Windows 10/11 build numbers to recognizable versions
        if result['major'] == '10':
            build = result.get('build', '')
            if build.isdigit():
                build_num = int(build)
                if build_num >= 22000:
                    result['marketing_version'] = 'Windows 11'
                elif build_num >= 19042:
                    result['marketing_version'] = 'Windows 10 20H2 or newer'
                elif build_num >= 19041:
                    result['marketing_version'] = 'Windows 10 2004'
                elif build_num >= 18363:
                    result['marketing_version'] = 'Windows 10 1909'
                else:
                    result['marketing_version'] = f"Windows 10 (Build {build})"
        
        return result
