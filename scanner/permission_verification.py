"""
Permission Verification System for ZtionSec
Ensures ethical scanning by verifying domain ownership and consent
"""

import requests
import dns.resolver
import whois
import socket
import re
import hashlib
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
import json

logger = logging.getLogger(__name__)

@dataclass
class PermissionResult:
    """Result of permission verification"""
    domain: str
    permission_granted: bool
    verification_method: str
    confidence_level: str  # high, medium, low
    verification_details: Dict[str, Any]
    restrictions: List[str]
    expires_at: Optional[datetime]
    verification_token: Optional[str]

class PermissionVerificationSystem:
    """Comprehensive permission verification for ethical scanning"""
    
    def __init__(self):
        self.verification_cache = {}
        self.whitelist_domains = set()
        self.blacklist_domains = set()
        self.rate_limits = {}
        self.load_domain_lists()
        
    def load_domain_lists(self):
        """Load pre-approved and restricted domain lists"""
        # Pre-approved domains (with explicit consent)
        self.whitelist_domains.update([
            'example.com',
            'test.com',
            'demo.ztionsec.com'
        ])
        
        # Restricted domains (never scan)
        self.blacklist_domains.update([
            'gov',
            'mil',
            'edu',
            'bank',
            'financial',
            'healthcare',
            'medical',
            'hospital'
        ])
    
    def verify_scanning_permission(self, target_url: str, user_info: Dict[str, Any] = None) -> PermissionResult:
        """
        Comprehensive permission verification for target URL
        
        Args:
            target_url: The URL to be scanned
            user_info: Information about the user requesting the scan
            
        Returns:
            PermissionResult with verification details
        """
        parsed_url = urlparse(target_url)
        domain = parsed_url.netloc.lower()
        
        # Remove www prefix for consistency
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check cache first
        cache_key = f"{domain}_{hashlib.md5(str(user_info).encode()).hexdigest()[:8]}"
        if cache_key in self.verification_cache:
            cached_result = self.verification_cache[cache_key]
            if cached_result.expires_at and cached_result.expires_at > datetime.now():
                return cached_result
        
        # Perform comprehensive verification
        verification_result = self._perform_verification(domain, target_url, user_info)
        
        # Cache the result
        self.verification_cache[cache_key] = verification_result
        
        return verification_result
    
    def _perform_verification(self, domain: str, target_url: str, user_info: Dict[str, Any]) -> PermissionResult:
        """Perform the actual permission verification"""
        
        # Step 1: Check blacklist
        if self._is_blacklisted(domain):
            return PermissionResult(
                domain=domain,
                permission_granted=False,
                verification_method='blacklist_check',
                confidence_level='high',
                verification_details={'reason': 'Domain is in restricted list'},
                restrictions=['scanning_prohibited'],
                expires_at=None,
                verification_token=None
            )
        
        # Step 2: Check whitelist
        if self._is_whitelisted(domain):
            return PermissionResult(
                domain=domain,
                permission_granted=True,
                verification_method='whitelist_check',
                confidence_level='high',
                verification_details={'reason': 'Domain is pre-approved'},
                restrictions=[],
                expires_at=datetime.now() + timedelta(days=30),
                verification_token=self._generate_verification_token(domain)
            )
        
        # Step 3: Check for explicit consent mechanisms
        consent_result = self._check_explicit_consent(domain, target_url)
        if consent_result['found']:
            return PermissionResult(
                domain=domain,
                permission_granted=True,
                verification_method='explicit_consent',
                confidence_level='high',
                verification_details=consent_result,
                restrictions=consent_result.get('restrictions', []),
                expires_at=datetime.now() + timedelta(days=7),
                verification_token=self._generate_verification_token(domain)
            )
        
        # Step 4: Domain ownership verification
        ownership_result = self._verify_domain_ownership(domain, user_info)
        if ownership_result['verified']:
            return PermissionResult(
                domain=domain,
                permission_granted=True,
                verification_method='ownership_verification',
                confidence_level='high',
                verification_details=ownership_result,
                restrictions=['limited_scope'],
                expires_at=datetime.now() + timedelta(days=1),
                verification_token=self._generate_verification_token(domain)
            )
        
        # Step 5: Check robots.txt for scanning permissions
        robots_result = self._check_robots_txt(target_url)
        if robots_result['scanning_allowed']:
            return PermissionResult(
                domain=domain,
                permission_granted=True,
                verification_method='robots_txt',
                confidence_level='medium',
                verification_details=robots_result,
                restrictions=['respect_robots_txt', 'limited_scope'],
                expires_at=datetime.now() + timedelta(hours=6),
                verification_token=self._generate_verification_token(domain)
            )
        
        # Step 6: Check security.txt for contact information
        security_txt_result = self._check_security_txt(target_url)
        if security_txt_result['found']:
            return PermissionResult(
                domain=domain,
                permission_granted=False,
                verification_method='security_txt_found',
                confidence_level='medium',
                verification_details=security_txt_result,
                restrictions=['contact_required'],
                expires_at=None,
                verification_token=None
            )
        
        # Step 7: Default restrictive approach
        return self._default_restricted_permission(domain, target_url)
    
    def _is_blacklisted(self, domain: str) -> bool:
        """Check if domain is in blacklist"""
        # Check exact domain
        if domain in self.blacklist_domains:
            return True
        
        # Check TLD restrictions
        tld = domain.split('.')[-1]
        if tld in self.blacklist_domains:
            return True
        
        # Check for sensitive keywords
        sensitive_keywords = ['gov', 'mil', 'bank', 'financial', 'medical', 'hospital', 'school']
        for keyword in sensitive_keywords:
            if keyword in domain.lower():
                return True
        
        return False
    
    def _is_whitelisted(self, domain: str) -> bool:
        """Check if domain is in whitelist"""
        return domain in self.whitelist_domains
    
    def _check_explicit_consent(self, domain: str, target_url: str) -> Dict[str, Any]:
        """Check for explicit scanning consent mechanisms"""
        consent_result = {
            'found': False,
            'method': None,
            'details': {},
            'restrictions': []
        }
        
        try:
            # Check for security scanning consent page
            consent_paths = [
                '/.well-known/security-scanning-policy',
                '/security-scanning-policy',
                '/scanning-consent',
                '/.well-known/security.txt'
            ]
            
            for path in consent_paths:
                consent_url = urljoin(target_url, path)
                try:
                    response = requests.get(consent_url, timeout=10, verify=False)
                    if response.status_code == 200:
                        content = response.text.lower()
                        
                        # Look for consent indicators
                        consent_indicators = [
                            'security scanning allowed',
                            'vulnerability scanning permitted',
                            'authorized security testing',
                            'scanning consent granted'
                        ]
                        
                        for indicator in consent_indicators:
                            if indicator in content:
                                consent_result['found'] = True
                                consent_result['method'] = f'consent_page_{path}'
                                consent_result['details'] = {
                                    'consent_url': consent_url,
                                    'consent_text': indicator,
                                    'full_content': content[:500]  # First 500 chars
                                }
                                
                                # Parse restrictions if any
                                if 'limited scope' in content:
                                    consent_result['restrictions'].append('limited_scope')
                                if 'rate limited' in content:
                                    consent_result['restrictions'].append('rate_limited')
                                
                                return consent_result
                
                except requests.RequestException:
                    continue
        
        except Exception as e:
            logger.error(f"Error checking explicit consent for {domain}: {str(e)}")
        
        return consent_result
    
    def _verify_domain_ownership(self, domain: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Verify if user owns the domain"""
        ownership_result = {
            'verified': False,
            'method': None,
            'details': {}
        }
        
        if not user_info:
            return ownership_result
        
        user_email = user_info.get('email', '')
        if not user_email:
            return ownership_result
        
        try:
            # Method 1: Check if email domain matches target domain
            email_domain = user_email.split('@')[-1].lower()
            if email_domain == domain:
                ownership_result['verified'] = True
                ownership_result['method'] = 'email_domain_match'
                ownership_result['details'] = {
                    'user_email': user_email,
                    'domain_match': True
                }
                return ownership_result
            
            # Method 2: Check WHOIS information
            try:
                whois_info = whois.whois(domain)
                if whois_info:
                    # Check registrant email
                    registrant_email = getattr(whois_info, 'emails', [])
                    if isinstance(registrant_email, str):
                        registrant_email = [registrant_email]
                    
                    if user_email.lower() in [email.lower() for email in registrant_email]:
                        ownership_result['verified'] = True
                        ownership_result['method'] = 'whois_email_match'
                        ownership_result['details'] = {
                            'whois_emails': registrant_email,
                            'user_email': user_email
                        }
                        return ownership_result
            
            except Exception as e:
                logger.warning(f"WHOIS lookup failed for {domain}: {str(e)}")
            
            # Method 3: DNS TXT record verification (for advanced users)
            try:
                txt_records = dns.resolver.resolve(domain, 'TXT')
                for record in txt_records:
                    record_text = str(record).strip('"')
                    if f'ztionsec-verify={user_email}' in record_text:
                        ownership_result['verified'] = True
                        ownership_result['method'] = 'dns_txt_verification'
                        ownership_result['details'] = {
                            'txt_record': record_text,
                            'user_email': user_email
                        }
                        return ownership_result
            
            except Exception as e:
                logger.warning(f"DNS TXT lookup failed for {domain}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error verifying domain ownership for {domain}: {str(e)}")
        
        return ownership_result
    
    def _check_robots_txt(self, target_url: str) -> Dict[str, Any]:
        """Check robots.txt for scanning permissions"""
        robots_result = {
            'scanning_allowed': False,
            'details': {},
            'restrictions': []
        }
        
        try:
            robots_url = urljoin(target_url, '/robots.txt')
            response = requests.get(robots_url, timeout=10)
            
            if response.status_code == 200:
                robots_content = response.text.lower()
                
                # Check for security scanner allowances
                scanner_allowances = [
                    'allow: /security-scan',
                    'allow: /vulnerability-scan',
                    'user-agent: security-scanner',
                    'user-agent: ztionsec'
                ]
                
                for allowance in scanner_allowances:
                    if allowance in robots_content:
                        robots_result['scanning_allowed'] = True
                        robots_result['details'] = {
                            'robots_url': robots_url,
                            'allowance_found': allowance,
                            'full_content': robots_content
                        }
                        break
                
                # Check for crawl-delay (rate limiting)
                crawl_delay_match = re.search(r'crawl-delay:\s*(\d+)', robots_content)
                if crawl_delay_match:
                    delay = int(crawl_delay_match.group(1))
                    robots_result['restrictions'].append(f'crawl_delay_{delay}')
                
                # Check for disallowed paths
                disallow_matches = re.findall(r'disallow:\s*([^\n\r]+)', robots_content)
                if disallow_matches:
                    robots_result['restrictions'].extend([f'disallow_{path.strip()}' for path in disallow_matches])
        
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {target_url}: {str(e)}")
        
        return robots_result
    
    def _check_security_txt(self, target_url: str) -> Dict[str, Any]:
        """Check security.txt for security contact information"""
        security_txt_result = {
            'found': False,
            'contact_info': [],
            'details': {}
        }
        
        try:
            # Check both standard locations
            security_txt_paths = [
                '/.well-known/security.txt',
                '/security.txt'
            ]
            
            for path in security_txt_paths:
                security_url = urljoin(target_url, path)
                try:
                    response = requests.get(security_url, timeout=10)
                    if response.status_code == 200:
                        content = response.text
                        
                        # Parse contact information
                        contact_matches = re.findall(r'Contact:\s*(.+)', content, re.IGNORECASE)
                        
                        if contact_matches:
                            security_txt_result['found'] = True
                            security_txt_result['contact_info'] = contact_matches
                            security_txt_result['details'] = {
                                'security_txt_url': security_url,
                                'full_content': content
                            }
                            return security_txt_result
                
                except requests.RequestException:
                    continue
        
        except Exception as e:
            logger.warning(f"Error checking security.txt for {target_url}: {str(e)}")
        
        return security_txt_result
    
    def _default_restricted_permission(self, domain: str, target_url: str) -> PermissionResult:
        """Default restrictive permission for unknown domains"""
        
        # Allow very limited scanning for public websites
        try:
            # Check if it's a public website
            response = requests.head(target_url, timeout=10)
            if response.status_code == 200:
                return PermissionResult(
                    domain=domain,
                    permission_granted=True,
                    verification_method='public_website_limited',
                    confidence_level='low',
                    verification_details={
                        'reason': 'Public website with limited scanning allowed',
                        'restrictions_applied': True
                    },
                    restrictions=[
                        'surface_scan_only',
                        'no_active_testing',
                        'respect_rate_limits',
                        'no_sensitive_data_access'
                    ],
                    expires_at=datetime.now() + timedelta(hours=1),
                    verification_token=self._generate_verification_token(domain, limited=True)
                )
        
        except Exception:
            pass
        
        # Default deny
        return PermissionResult(
            domain=domain,
            permission_granted=False,
            verification_method='default_deny',
            confidence_level='high',
            verification_details={
                'reason': 'No explicit permission found, scanning denied for safety'
            },
            restrictions=['scanning_prohibited'],
            expires_at=None,
            verification_token=None
        )
    
    def _generate_verification_token(self, domain: str, limited: bool = False) -> str:
        """Generate verification token for tracking"""
        timestamp = str(int(time.time()))
        token_data = f"{domain}_{timestamp}_{'limited' if limited else 'full'}"
        return hashlib.sha256(token_data.encode()).hexdigest()[:16]
    
    def check_scan_compliance(self, permission_result: PermissionResult, 
                            scan_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check if scan configuration complies with permissions"""
        
        if not permission_result.permission_granted:
            return False, ['Permission not granted for scanning']
        
        violations = []
        restrictions = permission_result.restrictions
        
        # Check scan scope restrictions
        if 'surface_scan_only' in restrictions:
            if scan_config.get('deep_scan', False):
                violations.append('Deep scanning not allowed - surface scan only')
            if scan_config.get('active_testing', False):
                violations.append('Active testing not allowed')
        
        if 'no_active_testing' in restrictions:
            if scan_config.get('active_testing', False):
                violations.append('Active vulnerability testing not permitted')
        
        if 'limited_scope' in restrictions:
            if scan_config.get('subdomain_scan', False):
                violations.append('Subdomain scanning not allowed')
            if scan_config.get('port_scan', False):
                violations.append('Port scanning not allowed')
        
        # Check rate limiting compliance
        if any('crawl_delay' in r for r in restrictions):
            crawl_delay = next((int(r.split('_')[-1]) for r in restrictions if 'crawl_delay' in r), 1)
            if scan_config.get('request_rate', 10) > (60 / crawl_delay):
                violations.append(f'Request rate too high - max {60 / crawl_delay} requests/minute')
        
        # Check path restrictions
        disallowed_paths = [r.replace('disallow_', '') for r in restrictions if r.startswith('disallow_')]
        scan_paths = scan_config.get('scan_paths', [])
        for path in scan_paths:
            for disallowed in disallowed_paths:
                if path.startswith(disallowed):
                    violations.append(f'Path {path} is disallowed by robots.txt')
        
        return len(violations) == 0, violations
    
    def log_permission_check(self, domain: str, permission_result: PermissionResult, 
                           user_info: Dict[str, Any] = None):
        """Log permission verification for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'domain': domain,
            'permission_granted': permission_result.permission_granted,
            'verification_method': permission_result.verification_method,
            'confidence_level': permission_result.confidence_level,
            'user_info': {
                'ip_address': user_info.get('ip_address') if user_info else None,
                'user_agent': user_info.get('user_agent') if user_info else None,
                'email': user_info.get('email') if user_info else None
            },
            'restrictions': permission_result.restrictions,
            'verification_token': permission_result.verification_token
        }
        
        logger.info(f"Permission verification: {json.dumps(log_entry)}")
    
    def get_permission_statistics(self) -> Dict[str, Any]:
        """Get statistics about permission verifications"""
        # In a real implementation, this would query a database
        return {
            'total_verifications': len(self.verification_cache),
            'granted_permissions': len([r for r in self.verification_cache.values() if r.permission_granted]),
            'denied_permissions': len([r for r in self.verification_cache.values() if not r.permission_granted]),
            'verification_methods': {},
            'most_common_restrictions': []
        }

class ScanningEthicsEnforcer:
    """Enforces ethical scanning practices"""
    
    def __init__(self, permission_system: PermissionVerificationSystem):
        self.permission_system = permission_system
        self.active_scans = {}
        self.scan_history = {}
    
    def authorize_scan(self, target_url: str, scan_config: Dict[str, Any], 
                      user_info: Dict[str, Any] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Authorize a scan request
        
        Returns:
            (authorized, reason, verification_token)
        """
        
        # Verify permissions
        permission_result = self.permission_system.verify_scanning_permission(target_url, user_info)
        
        if not permission_result.permission_granted:
            reason = f"Permission denied: {permission_result.verification_details.get('reason', 'Unknown')}"
            return False, reason, None
        
        # Check compliance
        compliant, violations = self.permission_system.check_scan_compliance(permission_result, scan_config)
        
        if not compliant:
            reason = f"Scan configuration violations: {'; '.join(violations)}"
            return False, reason, None
        
        # Log the authorization
        self.permission_system.log_permission_check(
            urlparse(target_url).netloc, 
            permission_result, 
            user_info
        )
        
        return True, "Scan authorized", permission_result.verification_token
    
    def enforce_scan_restrictions(self, verification_token: str, scan_action: str) -> bool:
        """Enforce restrictions during scan execution"""
        
        # Find the permission result by token
        permission_result = None
        for cached_result in self.permission_system.verification_cache.values():
            if cached_result.verification_token == verification_token:
                permission_result = cached_result
                break
        
        if not permission_result:
            return False
        
        # Check if action is allowed
        restrictions = permission_result.restrictions
        
        if scan_action == 'active_exploit_test' and 'no_active_testing' in restrictions:
            return False
        
        if scan_action == 'deep_directory_scan' and 'surface_scan_only' in restrictions:
            return False
        
        if scan_action == 'subdomain_enumeration' and 'limited_scope' in restrictions:
            return False
        
        return True
