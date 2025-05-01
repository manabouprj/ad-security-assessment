"""
Tests for the OS Detector module.
"""

import unittest
from src.utils.os_detector import OSDetector

class TestOSDetector(unittest.TestCase):
    """Test cases for the OSDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = OSDetector()
    
    def test_detect_os_type_windows_server(self):
        """Test detection of Windows Server OS."""
        os_type, version = self.detector.detect_os_type("Windows Server 2019")
        self.assertEqual(os_type, "windows_server")
        self.assertEqual(version, "2019")
    
    def test_detect_os_type_windows_client(self):
        """Test detection of Windows client OS."""
        os_type, version = self.detector.detect_os_type("Windows 10 Enterprise")
        self.assertEqual(os_type, "windows_client")
        self.assertEqual(version, "10")
    
    def test_detect_os_type_linux(self):
        """Test detection of Linux OS."""
        os_type, version = self.detector.detect_os_type("Linux Ubuntu 20.04")
        self.assertEqual(os_type, "linux")
        self.assertEqual(version, "20.04")
    
    def test_detect_os_type_unknown(self):
        """Test detection of unknown OS."""
        os_type, version = self.detector.detect_os_type("Unknown OS")
        self.assertEqual(os_type, "unknown")
        self.assertIsNone(version)
    
    def test_normalize_os_info_windows_server(self):
        """Test normalization of Windows Server OS info."""
        result = self.detector.normalize_os_info("Windows Server", "2019")
        self.assertEqual(result["type"], "windows_server")
        self.assertEqual(result["name"], "Windows Server")
        self.assertEqual(result["version"], "2019")
        self.assertEqual(result["full_name"], "Windows Server 2019")
    
    def test_normalize_os_info_windows_client(self):
        """Test normalization of Windows client OS info."""
        result = self.detector.normalize_os_info("Windows 10")
        self.assertEqual(result["type"], "windows_client")
        self.assertEqual(result["name"], "Windows")
        self.assertEqual(result["version"], "10")
        self.assertEqual(result["full_name"], "Windows 10")
    
    def test_is_server_os(self):
        """Test server OS detection."""
        self.assertTrue(self.detector.is_server_os("Windows Server 2019"))
        self.assertTrue(self.detector.is_server_os("Linux Server"))
        self.assertFalse(self.detector.is_server_os("Windows 10"))
    
    def test_get_os_family(self):
        """Test OS family detection."""
        self.assertEqual(self.detector.get_os_family("Windows Server 2019"), "Windows")
        self.assertEqual(self.detector.get_os_family("Windows 10"), "Windows")
        self.assertEqual(self.detector.get_os_family("Linux Ubuntu"), "Linux")
        self.assertEqual(self.detector.get_os_family("macOS Big Sur"), "macOS")
        self.assertEqual(self.detector.get_os_family("Unknown OS"), "Unknown")
    
    def test_parse_windows_version(self):
        """Test parsing of Windows version string."""
        result = self.detector.parse_windows_version("10.0.19042")
        self.assertEqual(result["major"], "10")
        self.assertEqual(result["minor"], "0")
        self.assertEqual(result["build"], "19042")
        self.assertTrue("marketing_version" in result)

if __name__ == "__main__":
    unittest.main()
