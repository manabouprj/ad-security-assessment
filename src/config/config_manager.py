"""
Configuration Manager

This module handles loading, validating, and managing configuration settings
for the Active Directory Security Assessment Agent.
"""

import logging
import os
import json
import socket
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages configuration settings for the application.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = {}
        self.default_config = {
            'domain': '',
            'server': '',
            'username': '',
            'password': '',
            'use_ssl': True,
            'verify_ssl': True,
            'port': 636,  # Default LDAPS port
            'sct_baselines_path': 'baselines',
            'max_computers_to_assess': 100,
            'assessment_timeout': 3600,  # 1 hour
            'report': {
                'company_name': '',
                'logo_path': '',
                'include_recommendations': True,
                'include_charts': True,
                'include_executive_summary': True
            }
        }
        
        logger.debug(f"Initialized configuration manager with config path: {config_path}")
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dictionary containing configuration settings
        """
        # Start with default configuration
        self.config = self.default_config.copy()
        
        # Try to load configuration from file
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                
                # Update configuration with values from file
                self._update_config_recursive(self.config, file_config)
                
                logger.info(f"Loaded configuration from {self.config_path}")
                
            except Exception as e:
                logger.error(f"Error loading configuration from {self.config_path}: {str(e)}", exc_info=True)
                logger.info("Using default configuration")
        else:
            logger.warning(f"Configuration file not found: {self.config_path}")
            logger.info("Using default configuration")
            
            # Create default configuration file
            self.save_config()
        
        # Validate and fill in missing values
        self._validate_and_fill_config()
        
        return self.config
    
    def _update_config_recursive(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively update configuration dictionary.
        
        Args:
            target: Target dictionary to update
            source: Source dictionary with new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively update nested dictionaries
                self._update_config_recursive(target[key], value)
            else:
                # Update value
                target[key] = value
    
    def _validate_and_fill_config(self) -> None:
        """Validate configuration and fill in missing values."""
        # Try to determine domain if not provided
        if not self.config.get('domain'):
            try:
                self.config['domain'] = socket.getfqdn().split('.', 1)[1]
                logger.info(f"Automatically determined domain: {self.config['domain']}")
            except (IndexError, socket.error):
                logger.warning("Could not automatically determine domain")
        
        # Try to determine server if not provided
        if not self.config.get('server'):
            try:
                # Try to find a domain controller
                if self.config.get('domain'):
                    # This is a placeholder - in a real implementation, we would
                    # use DNS to locate a domain controller
                    self.config['server'] = f"dc.{self.config['domain']}"
                    logger.info(f"Automatically determined server: {self.config['server']}")
            except Exception as e:
                logger.warning(f"Could not automatically determine server: {str(e)}")
        
        # Ensure baselines directory exists
        baselines_path = self.config.get('sct_baselines_path', 'baselines')
        os.makedirs(baselines_path, exist_ok=True)
    
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            config_dir = os.path.dirname(self.config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Saved configuration to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration to {self.config_path}: {str(e)}", exc_info=True)
            return False
    
    def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update configuration with new values.
        
        Args:
            new_config: Dictionary containing new configuration values
            
        Returns:
            Updated configuration dictionary
        """
        self._update_config_recursive(self.config, new_config)
        self._validate_and_fill_config()
        
        # Save updated configuration
        self.save_config()
        
        return self.config
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            default: Default value to return if key not found
            
        Returns:
            Configuration value or default if not found
        """
        # Handle nested keys with dot notation
        if '.' in key:
            parts = key.split('.')
            value = self.config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        
        # Simple key
        return self.config.get(key, default)
    
    def set_value(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            value: Value to set
        """
        # Handle nested keys with dot notation
        if '.' in key:
            parts = key.split('.')
            config = self.config
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            config[parts[-1]] = value
        else:
            # Simple key
            self.config[key] = value
