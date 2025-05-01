"""
Security Assessment Module

This module performs security assessments by comparing Active Directory configurations
with Microsoft Security Configuration Toolkit standards.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Tuple
import platform
from datetime import datetime

from src.core.ad_connector import ADConnector
from src.utils.sct_parser import SCTParser
from src.utils.os_detector import OSDetector

logger = logging.getLogger(__name__)

class SecurityAssessment:
    """
    Performs security assessments by comparing Active Directory configurations
    with Microsoft Security Configuration Toolkit standards.
    """
    
    def __init__(self, ad_connector: ADConnector, config: Dict[str, Any]):
        """
        Initialize the security assessment module.
        
        Args:
            ad_connector: Initialized ADConnector object
            config: Configuration dictionary
        """
        self.ad_connector = ad_connector
        self.config = config
        self.sct_parser = SCTParser(config.get('sct_baselines_path', 'baselines'))
        self.os_detector = OSDetector()
        self.assessment_results = {
            'timestamp': datetime.now().isoformat(),
            'domain': ad_connector.domain,
            'summary': {
                'total_checks': 0,
                'passed': 0,
                'failed': 0,
                'warning': 0,
                'not_applicable': 0
            },
            'domain_controllers': [],
            'computers': [],
            'domain_policies': {},
            'recommendations': []
        }
        
        logger.debug("Initialized security assessment module")
    
    def run_assessment(self) -> Dict[str, Any]:
        """
        Run the complete security assessment.
        
        Returns:
            Dictionary containing assessment results
        """
        logger.info("Starting security assessment")
        
        try:
            # Assess domain controllers
            self._assess_domain_controllers()
            
            # Assess member computers
            self._assess_computers()
            
            # Assess domain password policy
            self._assess_domain_password_policy()
            
            # Assess GPO settings
            self._assess_gpo_settings()
            
            # Generate recommendations
            self._generate_recommendations()
            
            # Update summary statistics
            self._update_summary_statistics()
            
            logger.info("Security assessment completed successfully")
            return self.assessment_results
            
        except Exception as e:
            logger.error(f"Error during security assessment: {str(e)}", exc_info=True)
            self.assessment_results['error'] = str(e)
            return self.assessment_results
    
    def _assess_domain_controllers(self) -> None:
        """Assess security of domain controllers."""
        logger.info("Assessing domain controllers")
        
        domain_controllers = self.ad_connector.get_domain_controllers()
        
        for dc in domain_controllers:
            dc_name = dc.get('name', 'Unknown')
            logger.info(f"Assessing domain controller: {dc_name}")
            
            # Get OS information
            os_info = dc.get('operatingSystem', '')
            os_version = dc.get('operatingSystemVersion', '')
            
            # Determine appropriate baseline based on OS
            baseline = self.sct_parser.get_baseline_for_os(os_info, os_version)
            
            if not baseline:
                logger.warning(f"No suitable baseline found for {dc_name} running {os_info} {os_version}")
                continue
            
            # Get security settings for this DC
            # In a real implementation, this would involve connecting to the DC
            # and retrieving actual security settings
            security_settings = self.ad_connector.get_computer_security_settings(dc_name)
            
            # Compare settings with baseline
            comparison_results = self._compare_with_baseline(security_settings, baseline)
            
            # Add results to assessment
            self.assessment_results['domain_controllers'].append({
                'name': dc_name,
                'os': os_info,
                'os_version': os_version,
                'baseline_used': baseline.get('name', 'Unknown'),
                'results': comparison_results
            })
    
    def _assess_computers(self) -> None:
        """Assess security of member computers."""
        logger.info("Assessing member computers")
        
        # Get all computers excluding domain controllers
        all_computers = self.ad_connector.get_computers()
        domain_controllers = self.ad_connector.get_domain_controllers()
        dc_names = [dc.get('name', '').lower() for dc in domain_controllers]
        
        member_computers = [comp for comp in all_computers 
                           if comp.get('name', '').lower() not in dc_names]
        
        # Sample a subset of computers if there are too many
        max_computers = self.config.get('max_computers_to_assess', 100)
        if len(member_computers) > max_computers:
            logger.info(f"Sampling {max_computers} computers out of {len(member_computers)}")
            # In a real implementation, we would use a more sophisticated sampling method
            member_computers = member_computers[:max_computers]
        
        for computer in member_computers:
            computer_name = computer.get('name', 'Unknown')
            logger.info(f"Assessing computer: {computer_name}")
            
            # Get OS information
            os_info = computer.get('operatingSystem', '')
            os_version = computer.get('operatingSystemVersion', '')
            
            # Determine appropriate baseline based on OS
            baseline = self.sct_parser.get_baseline_for_os(os_info, os_version)
            
            if not baseline:
                logger.warning(f"No suitable baseline found for {computer_name} running {os_info} {os_version}")
                continue
            
            # Get security settings for this computer
            security_settings = self.ad_connector.get_computer_security_settings(computer_name)
            
            # Compare settings with baseline
            comparison_results = self._compare_with_baseline(security_settings, baseline)
            
            # Add results to assessment
            self.assessment_results['computers'].append({
                'name': computer_name,
                'os': os_info,
                'os_version': os_version,
                'baseline_used': baseline.get('name', 'Unknown'),
                'results': comparison_results
            })
    
    def _assess_domain_password_policy(self) -> None:
        """Assess domain password policy."""
        logger.info("Assessing domain password policy")
        
        # Get domain password policy
        password_policy = self.ad_connector.get_domain_password_policy()
        
        # Get baseline password policy
        baseline = self.sct_parser.get_domain_password_policy_baseline()
        
        if not baseline:
            logger.warning("No baseline found for domain password policy")
            return
        
        # Compare with baseline
        comparison_results = self._compare_password_policy(password_policy, baseline)
        
        # Add results to assessment
        self.assessment_results['domain_policies']['password_policy'] = {
            'baseline_used': baseline.get('name', 'Default Password Policy'),
            'results': comparison_results
        }
    
    def _assess_gpo_settings(self) -> None:
        """Assess Group Policy Object settings."""
        logger.info("Assessing GPO settings")
        
        # Get all GPOs
        gpos = self.ad_connector.get_gpos()
        
        # In a real implementation, we would analyze each GPO's settings
        # For now, we'll just record the GPOs found
        self.assessment_results['domain_policies']['gpos'] = {
            'count': len(gpos),
            'gpos': [{'name': gpo.get('displayName', 'Unknown')} for gpo in gpos]
        }
        
        logger.info(f"Found {len(gpos)} GPOs")
    
    def _compare_with_baseline(self, settings: Dict[str, Any], 
                              baseline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Compare actual settings with baseline settings.
        
        Args:
            settings: Dictionary of actual settings
            baseline: Dictionary of baseline settings
            
        Returns:
            List of comparison results
        """
        # In a real implementation, this would do a detailed comparison
        # For now, we'll return a placeholder
        logger.warning("_compare_with_baseline is not fully implemented")
        
        # Simulate some comparison results
        return [
            {
                'setting_name': 'PasswordComplexity',
                'setting_path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Password Policy',
                'baseline_value': 'Enabled',
                'actual_value': 'Enabled',
                'status': 'pass',
                'severity': 'high'
            },
            {
                'setting_name': 'MinimumPasswordLength',
                'setting_path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Password Policy',
                'baseline_value': '14',
                'actual_value': '8',
                'status': 'fail',
                'severity': 'high'
            },
            {
                'setting_name': 'AccountLockoutThreshold',
                'setting_path': 'Computer Configuration\\Windows Settings\\Security Settings\\Account Policies\\Account Lockout Policy',
                'baseline_value': '5',
                'actual_value': '0',
                'status': 'fail',
                'severity': 'high'
            }
        ]
    
    def _compare_password_policy(self, policy: Dict[str, Any], 
                               baseline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Compare actual password policy with baseline policy.
        
        Args:
            policy: Dictionary of actual password policy settings
            baseline: Dictionary of baseline password policy settings
            
        Returns:
            List of comparison results
        """
        # In a real implementation, this would do a detailed comparison
        # For now, we'll return a placeholder
        logger.warning("_compare_password_policy is not fully implemented")
        
        # Simulate some comparison results
        return [
            {
                'setting_name': 'Minimum password length',
                'baseline_value': '14 characters',
                'actual_value': policy.get('minPwdLength', 'Unknown'),
                'status': 'fail' if policy.get('minPwdLength', 0) < 14 else 'pass',
                'severity': 'high'
            },
            {
                'setting_name': 'Password history',
                'baseline_value': '24 passwords remembered',
                'actual_value': policy.get('pwdHistoryLength', 'Unknown'),
                'status': 'fail' if policy.get('pwdHistoryLength', 0) < 24 else 'pass',
                'severity': 'medium'
            },
            {
                'setting_name': 'Maximum password age',
                'baseline_value': '60 days',
                'actual_value': policy.get('maxPwdAge', 'Unknown'),
                'status': 'warning',  # Would need conversion from AD's format
                'severity': 'medium'
            }
        ]
    
    def _generate_recommendations(self) -> None:
        """Generate security recommendations based on assessment results."""
        logger.info("Generating security recommendations")
        
        # In a real implementation, this would analyze all results and generate
        # tailored recommendations. For now, we'll use placeholders.
        
        # Check domain controllers
        for dc in self.assessment_results['domain_controllers']:
            for result in dc.get('results', []):
                if result.get('status') == 'fail':
                    self.assessment_results['recommendations'].append({
                        'target': f"Domain Controller: {dc.get('name')}",
                        'setting': result.get('setting_name'),
                        'recommendation': f"Change {result.get('setting_name')} from '{result.get('actual_value')}' to '{result.get('baseline_value')}'",
                        'severity': result.get('severity', 'medium'),
                        'reference': f"Microsoft Security Baseline for {dc.get('os')} {dc.get('os_version')}"
                    })
        
        # Check member computers
        for computer in self.assessment_results['computers']:
            for result in computer.get('results', []):
                if result.get('status') == 'fail':
                    self.assessment_results['recommendations'].append({
                        'target': f"Computer: {computer.get('name')}",
                        'setting': result.get('setting_name'),
                        'recommendation': f"Change {result.get('setting_name')} from '{result.get('actual_value')}' to '{result.get('baseline_value')}'",
                        'severity': result.get('severity', 'medium'),
                        'reference': f"Microsoft Security Baseline for {computer.get('os')} {computer.get('os_version')}"
                    })
        
        # Check domain password policy
        if 'password_policy' in self.assessment_results['domain_policies']:
            for result in self.assessment_results['domain_policies']['password_policy'].get('results', []):
                if result.get('status') == 'fail':
                    self.assessment_results['recommendations'].append({
                        'target': "Domain Password Policy",
                        'setting': result.get('setting_name'),
                        'recommendation': f"Change {result.get('setting_name')} from '{result.get('actual_value')}' to '{result.get('baseline_value')}'",
                        'severity': result.get('severity', 'medium'),
                        'reference': "Microsoft Security Baseline for Domain Password Policy"
                    })
        
        # Sort recommendations by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        self.assessment_results['recommendations'].sort(
            key=lambda x: severity_order.get(x.get('severity', 'low'), 3)
        )
        
        logger.info(f"Generated {len(self.assessment_results['recommendations'])} recommendations")
    
    def _update_summary_statistics(self) -> None:
        """Update summary statistics based on assessment results."""
        total_checks = 0
        passed = 0
        failed = 0
        warning = 0
        not_applicable = 0
        
        # Count domain controller results
        for dc in self.assessment_results['domain_controllers']:
            for result in dc.get('results', []):
                total_checks += 1
                status = result.get('status', '')
                if status == 'pass':
                    passed += 1
                elif status == 'fail':
                    failed += 1
                elif status == 'warning':
                    warning += 1
                elif status == 'not_applicable':
                    not_applicable += 1
        
        # Count member computer results
        for computer in self.assessment_results['computers']:
            for result in computer.get('results', []):
                total_checks += 1
                status = result.get('status', '')
                if status == 'pass':
                    passed += 1
                elif status == 'fail':
                    failed += 1
                elif status == 'warning':
                    warning += 1
                elif status == 'not_applicable':
                    not_applicable += 1
        
        # Count domain policy results
        if 'password_policy' in self.assessment_results['domain_policies']:
            for result in self.assessment_results['domain_policies']['password_policy'].get('results', []):
                total_checks += 1
                status = result.get('status', '')
                if status == 'pass':
                    passed += 1
                elif status == 'fail':
                    failed += 1
                elif status == 'warning':
                    warning += 1
                elif status == 'not_applicable':
                    not_applicable += 1
        
        # Update summary
        self.assessment_results['summary'] = {
            'total_checks': total_checks,
            'passed': passed,
            'failed': failed,
            'warning': warning,
            'not_applicable': not_applicable,
            'compliance_percentage': round(passed / total_checks * 100, 2) if total_checks > 0 else 0
        }
        
        logger.info(f"Assessment summary: {passed}/{total_checks} checks passed "
                   f"({self.assessment_results['summary']['compliance_percentage']}% compliance)")
