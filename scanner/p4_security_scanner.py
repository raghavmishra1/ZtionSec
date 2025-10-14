"""
P4 Category Security Scanner for ZtionSec
Comprehensive implementation of P4 security vulnerability detection
"""

import requests
import re
import json
import ssl
import socket
from urllib.parse import urlparse, urljoin
import hashlib
import time
from datetime import datetime

class P4SecurityScanner:
    def __init__(self, target_url):
        self.target_url = target_url
        self.parsed_url = urlparse(target_url)
        self.base_domain = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}"
        self.vulnerabilities = []
        
    def scan_all_p4_categories(self):
        """Run comprehensive P4 security scan"""
        results = {
            'ai_security': self.scan_ai_application_security(),
            'automotive': self.scan_automotive_security(),
            'broken_access': self.scan_broken_access_control(),
            'auth_session': self.scan_authentication_session(),
            'cloud_security': self.scan_cloud_security(),
            'xss': self.scan_cross_site_scripting(),
            'crypto': self.scan_cryptographic_weakness(),
            'data_storage': self.scan_insecure_data_storage(),
            'data_transport': self.scan_insecure_data_transport(),
            'security_config': self.scan_security_configuration(),
            'privacy': self.scan_privacy_concerns(),
            'data_exposure': self.scan_sensitive_data_exposure(),
            'server_config': self.scan_server_misconfiguration(),
            'injection': self.scan_server_side_injection(),
            'smart_contract': self.scan_smart_contract(),
            'redirects': self.scan_unvalidated_redirects()
        }
        return results
    
    def scan_ai_application_security(self):
        """P4: AI Application Security checks"""
        findings = []
        
        
        ai_endpoints = ['/api/ai', '/ml', '/predict', '/classify', '/chat', '/assistant']
        for endpoint in ai_endpoints:
            try:
                test_url = urljoin(self.base_domain, endpoint)
                
                payload = {"input": "<!--adversarial--> DROP TABLE users; --"}
                response = requests.post(test_url, json=payload, timeout=10)
                if response.status_code == 200:
                    findings.append({
                        'type': 'AI Misclassification Attack',
                        'severity': 'P4',
                        'endpoint': test_url,
                        'description': 'AI endpoint may be vulnerable to adversarial inputs'
                    })
            except:
                pass
                
      
        try:
            large_query = "A" * 10000
            response = requests.post(self.target_url, data={'query': large_query}, timeout=5)
            if response.status_code == 500:
                findings.append({
                    'type': 'AI DoS - Query Flooding',
                    'severity': 'P4',
                    'description': 'Large queries may cause AI service denial'
                })
        except:
            pass
            
        return findings
    
    def scan_automotive_security(self):
        """P4: Automotive Security Misconfiguration"""
        findings = []
        
        # Check for automotive-specific endpoints
        auto_endpoints = ['/can', '/obd', '/ecu', '/battery', '/gps', '/infotainment']
        for endpoint in auto_endpoints:
            try:
                test_url = urljoin(self.base_domain, endpoint)
                response = requests.get(test_url, timeout=10)
                if response.status_code == 200:
                    # Check for default credentials
                    if 'admin:admin' in response.text or 'root:root' in response.text:
                        findings.append({
                            'type': 'Automotive Default Credentials',
                            'severity': 'P4',
                            'endpoint': test_url,
                            'description': 'Default credentials found in automotive system'
                        })
            except:
                pass
                
        return findings
    
    def scan_broken_access_control(self):
        """P4: Broken Access Control checks"""
        findings = []
        
    
        guid_patterns = [
            '/user/12345678-1234-1234-1234-123456789012',
            '/profile/550e8400-e29b-41d4-a716-446655440000',
            '/account/6ba7b810-9dad-11d1-80b4-00c04fd430c8'
        ]
        
        for pattern in guid_patterns:
            try:
                test_url = urljoin(self.base_domain, pattern)
                response = requests.get(test_url, timeout=10)
                if response.status_code == 200:
                    findings.append({
                        'type': 'IDOR with Complex Object Identifiers',
                        'severity': 'P4',
                        'endpoint': test_url,
                        'description': 'Insecure Direct Object Reference with GUID/UUID'
                    })
            except:
                pass
                
     
        try:
            test_users = ['admin', 'test', 'user', 'demo']
            for user in test_users:
                response = requests.post(urljoin(self.base_domain, '/login'), 
                                       data={'username': user, 'password': 'wrong'}, timeout=10)
                if 'user not found' in response.text.lower():
                    findings.append({
                        'type': 'Username Enumeration',
                        'severity': 'P4',
                        'description': 'Username enumeration possible via error messages'
                    })
                    break
        except:
            pass
            
        return findings
    
    def scan_authentication_session(self):
        """P4: Authentication and Session Management"""
        findings = []
        
        try:
            response = requests.get(self.target_url, timeout=10)
            
            
            if 'set-cookie' in response.headers:
                cookies = response.headers['set-cookie']
                if 'secure' not in cookies.lower():
                    findings.append({
                        'type': 'Cleartext Session Token Transmission',
                        'severity': 'P4',
                        'description': 'Session cookies transmitted without Secure flag'
                    })
                    
            
            if self.parsed_url.scheme == 'http':
                login_endpoints = ['/login', '/signin', '/auth']
                for endpoint in login_endpoints:
                    test_url = urljoin(self.base_domain, endpoint)
                    try:
                        resp = requests.get(test_url, timeout=10)
                        if resp.status_code == 200 and 'password' in resp.text.lower():
                            findings.append({
                                'type': 'Weak Login Function Over HTTP',
                                'severity': 'P4',
                                'endpoint': test_url,
                                'description': 'Login form served over insecure HTTP'
                            })
                    except:
                        pass
                        
        except:
            pass
            
        return findings
    
    def scan_cloud_security(self):
        """P4: Cloud Security Misconfiguration"""
        findings = []
        
        
        api_endpoints = ['/api', '/v1', '/v2', '/graphql', '/swagger', '/docs']
        for endpoint in api_endpoints:
            try:
                test_url = urljoin(self.base_domain, endpoint)
                response = requests.get(test_url, timeout=10)
                if response.status_code == 200 and 'api' in response.text.lower():
                    findings.append({
                        'type': 'Insecure API Endpoints',
                        'severity': 'P4',
                        'endpoint': test_url,
                        'description': 'Potentially misconfigured API endpoint exposed'
                    })
            except:
                pass
                
        return findings
    
    def scan_cross_site_scripting(self):
        """P4: Cross-Site Scripting checks"""
        findings = []
        
       
        try:
            headers = {'Referer': '<script>alert("XSS")</script>'}
            response = requests.get(self.target_url, headers=headers, timeout=10)
            if '<script>alert("XSS")</script>' in response.text:
                findings.append({
                    'type': 'Referer XSS',
                    'severity': 'P4',
                    'description': 'XSS vulnerability via Referer header'
                })
        except:
            pass
        

        try:
            data_uri = 'data:text/html,<script>alert("XSS")</script>'
            response = requests.get(self.target_url, params={'url': data_uri}, timeout=10)
            if 'alert("XSS")' in response.text:
                findings.append({
                    'type': 'Data URI XSS',
                    'severity': 'P4',
                    'description': 'XSS vulnerability via Data URI'
                })
        except:
            pass
            
        return findings
    
    def scan_cryptographic_weakness(self):
        """P4: Cryptographic Weakness analysis"""
        findings = []
        
        try:
            
            context = ssl.create_default_context()
            with socket.create_connection((self.parsed_url.hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.parsed_url.hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    if not_after < datetime.now():
                        findings.append({
                            'type': 'Expired Cryptographic Certificate',
                            'severity': 'P4',
                            'description': f'SSL certificate expired on {not_after}'
                        })
                        
                    
                    cipher = ssock.cipher()
                    if cipher and ('RC4' in cipher[0] or 'DES' in cipher[0]):
                        findings.append({
                            'type': 'Vulnerable Cryptographic Library',
                            'severity': 'P4',
                            'description': f'Weak cipher suite in use: {cipher[0]}'
                        })
        except:
            pass
            
        return findings
    
    def scan_insecure_data_storage(self):
        """P4: Insecure Data Storage"""
        findings = []
        
        # Check for exposed backup files
        backup_files = ['/backup.sql', '/database.bak', '/config.txt', '/.env']
        for file_path in backup_files:
            try:
                test_url = urljoin(self.base_domain, file_path)
                response = requests.get(test_url, timeout=10)
                if response.status_code == 200:
                    findings.append({
                        'type': 'Sensitive Data Stored Unencrypted',
                        'severity': 'P4',
                        'endpoint': test_url,
                        'description': 'Backup file accessible containing sensitive data'
                    })
            except:
                pass
                
        return findings
    
    def scan_insecure_data_transport(self):
        """P4: Insecure Data Transport"""
        findings = []
        
        # Check for executable downloads without integrity check
        try:
            response = requests.get(self.target_url, timeout=10)
            if 'download' in response.text.lower():
                # Look for download links
                download_links = re.findall(r'href=["\']([^"\']*\.(exe|msi|dmg|pkg))["\']', response.text, re.IGNORECASE)
                for link, ext in download_links:
                    full_url = urljoin(self.base_domain, link)
                    dl_response = requests.head(full_url, timeout=10)
                    if 'content-md5' not in dl_response.headers and 'etag' not in dl_response.headers:
                        findings.append({
                            'type': 'Executable Download Without Integrity Check',
                            'severity': 'P4',
                            'endpoint': full_url,
                            'description': f'Executable download lacks integrity verification'
                        })
        except:
            pass
            
        return findings
    
    def scan_security_configuration(self):
        """P4: Security Configuration issues"""
        findings = []
        
        # Check for weak password policy
        try:
            register_endpoints = ['/register', '/signup', '/create-account']
            for endpoint in register_endpoints:
                test_url = urljoin(self.base_domain, endpoint)
                response = requests.get(test_url, timeout=10)
                if response.status_code == 200 and 'password' in response.text.lower():
                    # Test weak password acceptance
                    weak_passwords = ['123', 'password', 'admin']
                    for pwd in weak_passwords:
                        test_data = {'username': 'test', 'password': pwd}
                        reg_response = requests.post(test_url, data=test_data, timeout=10)
                        if 'success' in reg_response.text.lower() or reg_response.status_code == 201:
                            findings.append({
                                'type': 'No Password Policy',
                                'severity': 'P4',
                                'endpoint': test_url,
                                'description': 'Weak passwords accepted without policy enforcement'
                            })
                            break
        except:
            pass
            
        return findings
    
    def scan_privacy_concerns(self):
        """P4: Privacy Concerns"""
        findings = []
        
        # Check for unnecessary data collection
        try:
            response = requests.get(self.target_url, timeout=10)
            if 'wifi' in response.text.lower() and 'password' in response.text.lower():
                findings.append({
                    'type': 'Unnecessary Data Collection - WiFi Credentials',
                    'severity': 'P4',
                    'description': 'Application may be collecting WiFi SSID and passwords'
                })
        except:
            pass
            
        return findings
    
    def scan_sensitive_data_exposure(self):
        """P4: Sensitive Data Exposure"""
        findings = []
        
        try:
            response = requests.get(self.target_url, timeout=10)
            
            # Check for tokens in URL
            if 'token=' in self.target_url or 'key=' in self.target_url:
                findings.append({
                    'type': 'Sensitive Token in URL',
                    'severity': 'P4',
                    'description': 'Sensitive token exposed in URL parameters'
                })
                
            # Check for detailed error pages
            error_response = requests.get(urljoin(self.base_domain, '/nonexistent'), timeout=10)
            if 'apache' in error_response.text.lower() or 'nginx' in error_response.text.lower():
                findings.append({
                    'type': 'Detailed Server Configuration Exposure',
                    'severity': 'P4',
                    'description': 'Error pages reveal detailed server configuration'
                })
                
        except:
            pass
            
        return findings
    
    def scan_server_misconfiguration(self):
        """P4: Server Security Misconfiguration"""
        findings = []
        
        try:
            response = requests.get(self.target_url, timeout=10)
            headers = response.headers
            
            # Check for missing security headers
            security_headers = ['X-Frame-Options', 'X-Content-Type-Options', 'Cache-Control']
            for header in security_headers:
                if header not in headers:
                    findings.append({
                        'type': f'Missing Security Header - {header}',
                        'severity': 'P4',
                        'description': f'Security header {header} is missing'
                    })
                    
            # Check for clickjacking protection
            if 'X-Frame-Options' not in headers and 'Content-Security-Policy' not in headers:
                findings.append({
                    'type': 'Clickjacking Vulnerability',
                    'severity': 'P4',
                    'description': 'No clickjacking protection implemented'
                })
                
        except:
            pass
            
        return findings
    
    def scan_server_side_injection(self):
        """P4: Server-Side Injection"""
        findings = []
        
        # Test for SSTI
        ssti_payloads = ['{{7*7}}', '${7*7}', '#{7*7}']
        for payload in ssti_payloads:
            try:
                response = requests.post(self.target_url, data={'input': payload}, timeout=10)
                if '49' in response.text:
                    findings.append({
                        'type': 'Server-Side Template Injection (SSTI)',
                        'severity': 'P4',
                        'description': 'SSTI vulnerability detected via template expression'
                    })
                    break
            except:
                pass
                
        return findings
    
    def scan_smart_contract(self):
        """P4: Smart Contract Misconfiguration"""
        findings = []
        
        # Check for blockchain-related endpoints
        blockchain_endpoints = ['/contract', '/ethereum', '/web3', '/blockchain']
        for endpoint in blockchain_endpoints:
            try:
                test_url = urljoin(self.base_domain, endpoint)
                response = requests.get(test_url, timeout=10)
                if response.status_code == 200:
                    findings.append({
                        'type': 'Smart Contract Interface Detected',
                        'severity': 'P4',
                        'endpoint': test_url,
                        'description': 'Smart contract interface may have misconfigurations'
                    })
            except:
                pass
                
        return findings
    
    def scan_unvalidated_redirects(self):
        """P4: Unvalidated Redirects and Forwards"""
        findings = []
        
        # Test for open redirects
        redirect_params = ['redirect', 'url', 'next', 'return', 'goto']
        for param in redirect_params:
            try:
                test_url = f"{self.target_url}?{param}=http://evil.com"
                response = requests.get(test_url, timeout=10, allow_redirects=False)
                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location', '')
                    if 'evil.com' in location:
                        findings.append({
                            'type': 'Open Redirect - GET-Based',
                            'severity': 'P4',
                            'parameter': param,
                            'description': f'Open redirect vulnerability via {param} parameter'
                        })
            except:
                pass
                
        return findings
