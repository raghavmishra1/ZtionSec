"""
Legal Compliance and Terms Enforcement System for ZtionSec
Ensures proper terms of service enforcement and legal compliance
"""

import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
import logging
import re
from django.core.cache import cache
from django.conf import settings
import requests

logger = logging.getLogger(__name__)

@dataclass
class ComplianceViolation:
    """Represents a compliance violation"""
    violation_type: str
    severity: str  # critical, high, medium, low
    description: str
    user_identifier: str
    timestamp: datetime
    evidence: Dict[str, Any]
    action_taken: str
    resolved: bool = False

@dataclass
class UserConsent:
    """Tracks user consent and agreement to terms"""
    user_identifier: str
    consent_type: str  # terms_of_service, privacy_policy, scanning_agreement
    consent_version: str
    consent_timestamp: datetime
    ip_address: str
    user_agent: str
    explicit_consent: bool
    consent_method: str  # checkbox, digital_signature, api_agreement

class LegalComplianceSystem:
    """Comprehensive legal compliance and enforcement system"""
    
    def __init__(self):
        self.current_terms_version = "2025.1.0"
        self.current_privacy_version = "2025.1.0"
        self.consent_cache = {}
        self.violation_log = []
        self.compliance_rules = self._load_compliance_rules()
        
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules and regulations"""
        return {
            'gdpr': {
                'enabled': True,
                'data_retention_days': 365,
                'consent_required': True,
                'right_to_deletion': True,
                'data_portability': True
            },
            'ccpa': {
                'enabled': True,
                'opt_out_required': True,
                'data_disclosure': True,
                'consumer_rights': True
            },
            'scanning_ethics': {
                'permission_required': True,
                'rate_limiting': True,
                'no_malicious_use': True,
                'responsible_disclosure': True
            },
            'terms_enforcement': {
                'version_tracking': True,
                'explicit_acceptance': True,
                'change_notification': True,
                'violation_tracking': True
            }
        }
    
    def verify_user_consent(self, user_identifier: str, consent_type: str, 
                           request_info: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verify if user has provided valid consent
        
        Args:
            user_identifier: Unique identifier for the user
            consent_type: Type of consent (terms_of_service, privacy_policy, etc.)
            request_info: Information about the request (IP, user agent, etc.)
            
        Returns:
            (consent_valid, reason)
        """
        
        # Check if consent exists
        consent_key = f"{user_identifier}_{consent_type}"
        consent_record = self.consent_cache.get(consent_key)
        
        if not consent_record:
            return False, f"No {consent_type} consent found for user"
        
        # Check if consent is current version
        current_version = self._get_current_version(consent_type)
        if consent_record.consent_version != current_version:
            return False, f"Consent is for outdated version. Current: {current_version}, User: {consent_record.consent_version}"
        
        # Check if consent has expired
        if self._is_consent_expired(consent_record):
            return False, "Consent has expired and needs renewal"
        
        # Check if consent was explicit
        if not consent_record.explicit_consent:
            return False, "Explicit consent required but not provided"
        
        return True, "Valid consent found"
    
    def record_user_consent(self, user_identifier: str, consent_type: str, 
                           request_info: Dict[str, Any], explicit: bool = True) -> UserConsent:
        """Record user consent with full audit trail"""
        
        consent_record = UserConsent(
            user_identifier=user_identifier,
            consent_type=consent_type,
            consent_version=self._get_current_version(consent_type),
            consent_timestamp=datetime.now(),
            ip_address=request_info.get('ip_address', ''),
            user_agent=request_info.get('user_agent', ''),
            explicit_consent=explicit,
            consent_method=request_info.get('consent_method', 'web_form')
        )
        
        # Store consent record
        consent_key = f"{user_identifier}_{consent_type}"
        self.consent_cache[consent_key] = consent_record
        
        # Log consent for audit trail
        logger.info(f"User consent recorded: {consent_key} - Version: {consent_record.consent_version}")
        
        return consent_record
    
    def enforce_terms_compliance(self, user_identifier: str, action: str, 
                               action_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Enforce terms of service compliance for user actions
        
        Args:
            user_identifier: User performing the action
            action: Type of action (scan_website, api_request, etc.)
            action_data: Data about the action
            
        Returns:
            (allowed, violations)
        """
        
        violations = []
        
        # Check if user has accepted current terms
        consent_valid, consent_reason = self.verify_user_consent(
            user_identifier, 'terms_of_service', action_data
        )
        
        if not consent_valid:
            violations.append(f"Terms of service consent required: {consent_reason}")
        
        # Check action-specific compliance
        action_violations = self._check_action_compliance(action, action_data, user_identifier)
        violations.extend(action_violations)
        
        # Check rate limiting compliance
        rate_violations = self._check_rate_limiting_compliance(user_identifier, action, action_data)
        violations.extend(rate_violations)
        
        # Check scanning permission compliance
        if action in ['scan_website', 'vulnerability_scan', 'port_scan']:
            permission_violations = self._check_scanning_permission_compliance(action_data)
            violations.extend(permission_violations)
        
        # Log violations if any
        if violations:
            self._log_compliance_violation(user_identifier, action, violations, action_data)
        
        return len(violations) == 0, violations
    
    def _check_action_compliance(self, action: str, action_data: Dict[str, Any], 
                               user_identifier: str) -> List[str]:
        """Check compliance for specific actions"""
        violations = []
        
        if action == 'scan_website':
            target_url = action_data.get('target_url', '')
            
            # Check if URL is blacklisted
            if self._is_url_blacklisted(target_url):
                violations.append(f"Target URL {target_url} is in restricted list")
            
            # Check if user has permission to scan this domain
            domain = urlparse(target_url).netloc
            if not self._has_scanning_permission(user_identifier, domain):
                violations.append(f"No scanning permission for domain {domain}")
            
            # Check scan frequency limits
            if self._exceeds_scan_frequency(user_identifier, domain):
                violations.append(f"Scan frequency limit exceeded for domain {domain}")
        
        elif action == 'api_request':
            # Check API usage limits
            if self._exceeds_api_limits(user_identifier):
                violations.append("API usage limits exceeded")
            
            # Check API key validity
            api_key = action_data.get('api_key')
            if api_key and not self._is_valid_api_key(api_key, user_identifier):
                violations.append("Invalid or expired API key")
        
        elif action == 'data_export':
            # Check data export permissions
            if not self._has_data_export_permission(user_identifier):
                violations.append("Data export not permitted for this user")
        
        return violations
    
    def _check_rate_limiting_compliance(self, user_identifier: str, action: str, 
                                      action_data: Dict[str, Any]) -> List[str]:
        """Check rate limiting compliance"""
        violations = []
        
        # Define rate limits per action type
        rate_limits = {
            'scan_website': {'limit': 10, 'period': 3600},  # 10 scans per hour
            'api_request': {'limit': 100, 'period': 3600},   # 100 API calls per hour
            'breach_check': {'limit': 20, 'period': 3600},   # 20 breach checks per hour
        }
        
        if action in rate_limits:
            limit_config = rate_limits[action]
            current_usage = self._get_current_usage(user_identifier, action, limit_config['period'])
            
            if current_usage >= limit_config['limit']:
                violations.append(f"Rate limit exceeded for {action}: {current_usage}/{limit_config['limit']} per hour")
        
        return violations
    
    def _check_scanning_permission_compliance(self, action_data: Dict[str, Any]) -> List[str]:
        """Check scanning permission compliance"""
        violations = []
        
        target_url = action_data.get('target_url', '')
        if not target_url:
            return violations
        
        domain = urlparse(target_url).netloc.lower()
        
        # Check for government/military domains
        restricted_tlds = ['.gov', '.mil', '.edu']
        if any(domain.endswith(tld) for tld in restricted_tlds):
            violations.append(f"Scanning of {domain} is prohibited (restricted TLD)")
        
        # Check for financial/healthcare domains
        sensitive_keywords = ['bank', 'financial', 'medical', 'hospital', 'healthcare']
        if any(keyword in domain for keyword in sensitive_keywords):
            violations.append(f"Scanning of {domain} requires special authorization (sensitive sector)")
        
        # Check for explicit scanning consent
        if not self._has_explicit_scanning_consent(target_url):
            violations.append(f"No explicit scanning consent found for {domain}")
        
        return violations
    
    def _is_url_blacklisted(self, url: str) -> bool:
        """Check if URL is in blacklist"""
        blacklisted_domains = [
            'localhost',
            '127.0.0.1',
            '0.0.0.0',
            'internal',
            'intranet'
        ]
        
        domain = urlparse(url).netloc.lower()
        return any(blocked in domain for blocked in blacklisted_domains)
    
    def _has_scanning_permission(self, user_identifier: str, domain: str) -> bool:
        """Check if user has permission to scan domain"""
        # In a real implementation, this would check a database of permissions
        # For now, we'll implement basic checks
        
        # Check if user owns the domain (email domain match)
        user_email = self._get_user_email(user_identifier)
        if user_email:
            email_domain = user_email.split('@')[-1].lower()
            if email_domain == domain.lower():
                return True
        
        # Check if domain is in user's authorized list
        authorized_domains = self._get_authorized_domains(user_identifier)
        return domain.lower() in [d.lower() for d in authorized_domains]
    
    def _exceeds_scan_frequency(self, user_identifier: str, domain: str) -> bool:
        """Check if scan frequency is exceeded"""
        # Maximum 1 scan per domain per hour
        cache_key = f"scan_frequency_{user_identifier}_{domain}"
        last_scan = cache.get(cache_key)
        
        if last_scan:
            time_since_last = time.time() - last_scan
            if time_since_last < 3600:  # 1 hour
                return True
        
        # Record current scan time
        cache.set(cache_key, time.time(), 3600)
        return False
    
    def _exceeds_api_limits(self, user_identifier: str) -> bool:
        """Check if API limits are exceeded"""
        cache_key = f"api_usage_{user_identifier}"
        current_usage = cache.get(cache_key, 0)
        
        # Limit: 100 API calls per hour
        if current_usage >= 100:
            return True
        
        # Increment usage
        cache.set(cache_key, current_usage + 1, 3600)
        return False
    
    def _has_explicit_scanning_consent(self, target_url: str) -> bool:
        """Check for explicit scanning consent"""
        try:
            # Check for security.txt or scanning policy
            consent_paths = [
                '/.well-known/security.txt',
                '/.well-known/security-scanning-policy',
                '/security-scanning-policy'
            ]
            
            for path in consent_paths:
                consent_url = target_url.rstrip('/') + path
                try:
                    response = requests.get(consent_url, timeout=5, verify=False)
                    if response.status_code == 200:
                        content = response.text.lower()
                        consent_indicators = [
                            'security scanning allowed',
                            'vulnerability scanning permitted',
                            'authorized security testing'
                        ]
                        if any(indicator in content for indicator in consent_indicators):
                            return True
                except:
                    continue
        except:
            pass
        
        return False
    
    def _get_current_version(self, consent_type: str) -> str:
        """Get current version for consent type"""
        versions = {
            'terms_of_service': self.current_terms_version,
            'privacy_policy': self.current_privacy_version,
            'scanning_agreement': '2025.1.0'
        }
        return versions.get(consent_type, '1.0.0')
    
    def _is_consent_expired(self, consent_record: UserConsent) -> bool:
        """Check if consent has expired"""
        # Consent expires after 1 year
        expiry_date = consent_record.consent_timestamp + timedelta(days=365)
        return datetime.now() > expiry_date
    
    def _get_current_usage(self, user_identifier: str, action: str, period: int) -> int:
        """Get current usage for rate limiting"""
        cache_key = f"usage_{action}_{user_identifier}"
        usage_data = cache.get(cache_key, [])
        
        # Filter usage within the period
        current_time = time.time()
        recent_usage = [timestamp for timestamp in usage_data if current_time - timestamp < period]
        
        # Update cache with recent usage
        cache.set(cache_key, recent_usage, period)
        
        return len(recent_usage)
    
    def _log_compliance_violation(self, user_identifier: str, action: str, 
                                violations: List[str], action_data: Dict[str, Any]):
        """Log compliance violation for audit"""
        violation = ComplianceViolation(
            violation_type=action,
            severity=self._determine_violation_severity(violations),
            description='; '.join(violations),
            user_identifier=user_identifier,
            timestamp=datetime.now(),
            evidence=action_data,
            action_taken=self._determine_action(violations)
        )
        
        self.violation_log.append(violation)
        
        # Log to system logger
        logger.warning(f"Compliance violation: {user_identifier} - {action} - {violations}")
    
    def _determine_violation_severity(self, violations: List[str]) -> str:
        """Determine severity of violations"""
        critical_keywords = ['prohibited', 'restricted', 'unauthorized']
        high_keywords = ['permission', 'consent', 'blacklisted']
        
        for violation in violations:
            violation_lower = violation.lower()
            if any(keyword in violation_lower for keyword in critical_keywords):
                return 'critical'
            elif any(keyword in violation_lower for keyword in high_keywords):
                return 'high'
        
        return 'medium'
    
    def _determine_action(self, violations: List[str]) -> str:
        """Determine action to take for violations"""
        severity_actions = {
            'critical': 'block_immediately',
            'high': 'require_verification',
            'medium': 'warn_user',
            'low': 'log_only'
        }
        
        severity = self._determine_violation_severity(violations)
        return severity_actions.get(severity, 'log_only')
    
    def _get_user_email(self, user_identifier: str) -> Optional[str]:
        """Get user email for verification"""
        # In a real implementation, this would query the user database
        # For now, return None to indicate no email found
        return None
    
    def _get_authorized_domains(self, user_identifier: str) -> List[str]:
        """Get list of domains user is authorized to scan"""
        # In a real implementation, this would query the database
        return []
    
    def _has_data_export_permission(self, user_identifier: str) -> bool:
        """Check if user has data export permission"""
        # In a real implementation, check user permissions
        return True
    
    def _is_valid_api_key(self, api_key: str, user_identifier: str) -> bool:
        """Validate API key"""
        # In a real implementation, validate against database
        return True
    
    def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report for audit purposes"""
        
        # Filter violations by date range
        period_violations = [
            v for v in self.violation_log 
            if start_date <= v.timestamp <= end_date
        ]
        
        # Calculate statistics
        total_violations = len(period_violations)
        severity_counts = {}
        violation_types = {}
        
        for violation in period_violations:
            # Count by severity
            severity = violation.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Count by type
            v_type = violation.violation_type
            violation_types[v_type] = violation_types.get(v_type, 0) + 1
        
        # Calculate consent statistics
        total_consents = len(self.consent_cache)
        expired_consents = len([
            c for c in self.consent_cache.values() 
            if self._is_consent_expired(c)
        ])
        
        return {
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'violations': {
                'total': total_violations,
                'by_severity': severity_counts,
                'by_type': violation_types,
                'details': [
                    {
                        'timestamp': v.timestamp.isoformat(),
                        'type': v.violation_type,
                        'severity': v.severity,
                        'description': v.description,
                        'user': v.user_identifier,
                        'action_taken': v.action_taken
                    }
                    for v in period_violations
                ]
            },
            'consent_management': {
                'total_consents': total_consents,
                'expired_consents': expired_consents,
                'consent_compliance_rate': (total_consents - expired_consents) / max(total_consents, 1) * 100
            },
            'compliance_rules': self.compliance_rules,
            'recommendations': self._generate_compliance_recommendations(period_violations)
        }
    
    def _generate_compliance_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []
        
        if not violations:
            recommendations.append("Excellent compliance - no violations detected")
            return recommendations
        
        # Analyze violation patterns
        severity_counts = {}
        type_counts = {}
        
        for violation in violations:
            severity_counts[violation.severity] = severity_counts.get(violation.severity, 0) + 1
            type_counts[violation.violation_type] = type_counts.get(violation.violation_type, 0) + 1
        
        # Generate specific recommendations
        if severity_counts.get('critical', 0) > 0:
            recommendations.append("URGENT: Address critical violations immediately to prevent service suspension")
        
        if severity_counts.get('high', 0) > 5:
            recommendations.append("High number of high-severity violations - review user training and access controls")
        
        if type_counts.get('scan_website', 0) > 10:
            recommendations.append("Frequent scanning violations - implement better permission verification")
        
        if type_counts.get('api_request', 0) > 20:
            recommendations.append("API abuse detected - consider implementing stricter rate limiting")
        
        return recommendations

class DataRetentionManager:
    """Manages data retention and privacy compliance"""
    
    def __init__(self):
        self.retention_policies = {
            'scan_results': 365,  # days
            'user_data': 1095,    # 3 years
            'logs': 730,          # 2 years
            'consent_records': 2555,  # 7 years (legal requirement)
            'violation_logs': 1825    # 5 years
        }
    
    def apply_retention_policy(self, data_type: str) -> Dict[str, Any]:
        """Apply data retention policy"""
        retention_days = self.retention_policies.get(data_type, 365)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # In a real implementation, this would delete old data from database
        return {
            'data_type': data_type,
            'retention_days': retention_days,
            'cutoff_date': cutoff_date.isoformat(),
            'action': 'data_cleanup_scheduled'
        }
    
    def handle_deletion_request(self, user_identifier: str, data_types: List[str]) -> Dict[str, Any]:
        """Handle user data deletion request (GDPR Right to be Forgotten)"""
        
        deletion_results = {}
        
        for data_type in data_types:
            try:
                # In a real implementation, delete user data from database
                deletion_results[data_type] = {
                    'status': 'deleted',
                    'timestamp': datetime.now().isoformat(),
                    'records_affected': 0  # Would be actual count
                }
            except Exception as e:
                deletion_results[data_type] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return {
            'user_identifier': user_identifier,
            'deletion_request_id': hashlib.md5(f"{user_identifier}_{time.time()}".encode()).hexdigest(),
            'results': deletion_results,
            'completion_status': 'completed' if all(r['status'] == 'deleted' for r in deletion_results.values()) else 'partial'
        }
