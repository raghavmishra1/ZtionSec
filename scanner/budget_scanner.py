"""
Budget-Friendly Security Scanner
Focuses on P4 category vulnerabilities that are easy to find and fix
Perfect for security researchers on a budget
"""

import requests
import re
import urllib.parse
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class BudgetFinding:
    severity: str = "low"  # P4 category - low severity but easy to find
    category: str = "information_disclosure"
    title: str = ""
    description: str = ""
    recommendation: str = ""
    proof_of_concept: str = ""
    bounty_potential: str = "low"  # Expected bounty range
    difficulty: str = "easy"  # Easy to find and exploit

class BudgetSecurityScanner:
    """Scanner focused on easy-to-find P4 vulnerabilities for budget researchers"""
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ZtionSec-BudgetScanner/1.0'
        })
        # Set reasonable timeouts to prevent worker timeouts
        self.session.timeout = 5
        self.findings: List[BudgetFinding] = []
        
    def scan_all_budget_issues(self) -> List[BudgetFinding]:
        """Scan for all budget-friendly P4 vulnerabilities"""
        print(f"🔍 Starting budget security scan for {self.target_url}")
        
        # Easy information disclosure issues
        self.check_directory_listing()
        self.check_backup_files()
        self.check_config_files()
        self.check_debug_information()
        self.check_version_disclosure()
        self.check_email_disclosure()
        self.check_path_disclosure()
        self.check_server_status_pages()
        self.check_robots_txt_secrets()
        self.check_sitemap_information()
        self.check_comments_disclosure()
        self.check_error_pages()
        self.check_admin_panels()
        self.check_test_files()
        self.check_development_files()
        
        print(f"✅ Budget scan completed. Found {len(self.findings)} easy issues!")
        
        # Cleanup session to free memory
        self.cleanup()
        
        return self.findings
    
    def cleanup(self):
        """Clean up resources to free memory"""
        try:
            if hasattr(self, 'session'):
                self.session.close()
        except Exception:
            pass
    
    def check_directory_listing(self):
        """Check for directory listing vulnerabilities"""
        common_dirs = [
            '/admin/', '/backup/', '/config/', '/test/', '/dev/',
            '/uploads/', '/files/', '/images/', '/docs/', '/temp/',
            '/cache/', '/logs/', '/includes/', '/assets/', '/static/'
        ]
        
        for directory in common_dirs:
            try:
                url = urllib.parse.urljoin(self.target_url, directory)
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    # Check for directory listing indicators
                    if any(indicator in response.text.lower() for indicator in [
                        'index of', 'directory listing', 'parent directory',
                        '<title>index of', 'apache', 'nginx'
                    ]):
                        self.findings.append(BudgetFinding(
                            title=f"Directory Listing Enabled - {directory}",
                            description=f"Directory listing is enabled for {directory}, exposing internal structure",
                            recommendation="Disable directory listing in web server configuration",
                            proof_of_concept=f"GET {url} returns directory contents",
                            bounty_potential="$50-200",
                            category="information_disclosure"
                        ))
            except:
                continue
    
    def check_backup_files(self):
        """Check for backup files that might contain sensitive information"""
        base_url = self.target_url.rstrip('/')
        backup_extensions = [
            '.bak', '.backup', '.old', '.orig', '.copy', '.tmp',
            '.save', '~', '.swp', '.swo', '.zip', '.tar.gz'
        ]
        
        common_files = [
            'index', 'config', 'database', 'db', 'admin', 'login',
            'user', 'users', 'password', 'passwords', 'secret', 'secrets'
        ]
        
        for file_name in common_files:
            for ext in backup_extensions:
                try:
                    test_url = f"{base_url}/{file_name}{ext}"
                    response = self.session.get(test_url, timeout=3)
                    
                    if response.status_code == 200 and len(response.content) > 100:
                        self.findings.append(BudgetFinding(
                            title=f"Backup File Exposed - {file_name}{ext}",
                            description=f"Backup file {file_name}{ext} is publicly accessible",
                            recommendation="Remove backup files from web-accessible directories",
                            proof_of_concept=f"GET {test_url} returns {len(response.content)} bytes",
                            bounty_potential="$100-500",
                            category="information_disclosure"
                        ))
                except:
                    continue
    
    def check_config_files(self):
        """Check for exposed configuration files"""
        config_files = [
            '.env', '.env.local', '.env.production', 'config.php', 'config.json',
            'web.config', 'app.config', 'database.yml', 'settings.py',
            'wp-config.php', 'configuration.php', '.htaccess', '.htpasswd'
        ]
        
        for config_file in config_files:
            try:
                url = urllib.parse.urljoin(self.target_url, config_file)
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    # Check for configuration indicators
                    sensitive_patterns = [
                        'password', 'secret', 'key', 'token', 'api_key',
                        'database', 'mysql', 'postgres', 'mongodb'
                    ]
                    
                    if any(pattern in response.text.lower() for pattern in sensitive_patterns):
                        self.findings.append(BudgetFinding(
                            title=f"Configuration File Exposed - {config_file}",
                            description=f"Configuration file {config_file} contains sensitive information",
                            recommendation="Move configuration files outside web root or restrict access",
                            proof_of_concept=f"GET {url} exposes configuration data",
                            bounty_potential="$200-1000",
                            category="information_disclosure"
                        ))
            except:
                continue
    
    def check_debug_information(self):
        """Check for debug information disclosure"""
        debug_params = ['debug=1', 'debug=true', 'test=1', 'dev=1']
        
        for param in debug_params:
            try:
                debug_url = f"{self.target_url}?{param}"
                response = self.session.get(debug_url, timeout=5)
                
                debug_indicators = [
                    'stack trace', 'error trace', 'debug info', 'var_dump',
                    'print_r', 'exception', 'traceback', 'debug mode'
                ]
                
                if any(indicator in response.text.lower() for indicator in debug_indicators):
                    self.findings.append(BudgetFinding(
                        title=f"Debug Information Disclosure - {param}",
                        description=f"Debug parameter {param} exposes internal application details",
                        recommendation="Disable debug mode in production and sanitize error messages",
                        proof_of_concept=f"GET {debug_url} returns debug information",
                        bounty_potential="$50-300",
                        category="information_disclosure"
                    ))
            except:
                continue
    
    def check_version_disclosure(self):
        """Check for version information disclosure"""
        try:
            response = self.session.get(self.target_url, timeout=10)
            
            # Check headers for version information
            version_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version', 'X-Generator']
            
            for header in version_headers:
                if header in response.headers:
                    value = response.headers[header]
                    if any(char.isdigit() for char in value):  # Contains version numbers
                        self.findings.append(BudgetFinding(
                            title=f"Version Information Disclosure - {header}",
                            description=f"Server header {header} reveals version: {value}",
                            recommendation="Configure server to hide version information",
                            proof_of_concept=f"HTTP header {header}: {value}",
                            bounty_potential="$25-100",
                            category="information_disclosure"
                        ))
            
            # Check HTML for version comments
            version_patterns = [
                r'<!--.*version.*?(\d+\.\d+).*?-->',
                r'<!--.*v(\d+\.\d+).*?-->',
                r'generator.*?content="([^"]*\d+\.\d+[^"]*)"'
            ]
            
            for pattern in version_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    self.findings.append(BudgetFinding(
                        title="Version Information in HTML Comments",
                        description=f"HTML contains version information: {match}",
                        recommendation="Remove version information from HTML comments",
                        proof_of_concept=f"HTML source contains: {match}",
                        bounty_potential="$25-150",
                        category="information_disclosure"
                    ))
        except:
            pass
    
    def check_email_disclosure(self):
        """Check for email address disclosure"""
        try:
            response = self.session.get(self.target_url, timeout=10)
            
            # Find email addresses in the page
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, response.text)
            
            if emails:
                unique_emails = list(set(emails))
                if len(unique_emails) > 3:  # Multiple emails found
                    self.findings.append(BudgetFinding(
                        title="Multiple Email Addresses Disclosed",
                        description=f"Found {len(unique_emails)} email addresses on the page",
                        recommendation="Consider using contact forms instead of exposing email addresses",
                        proof_of_concept=f"Emails found: {', '.join(unique_emails[:3])}...",
                        bounty_potential="$25-100",
                        category="information_disclosure"
                    ))
        except:
            pass
    
    def check_path_disclosure(self):
        """Check for internal path disclosure"""
        try:
            # Try to trigger error pages that might reveal paths
            error_urls = [
                self.target_url + '/nonexistent-page-12345',
                self.target_url + '/../../../etc/passwd',
                self.target_url + '/admin/config.php'
            ]
            
            for url in error_urls:
                response = self.session.get(url, timeout=5)
                
                # Look for path disclosure patterns
                path_patterns = [
                    r'(/var/www/[^\s<>"\']+)',
                    r'(/home/[^\s<>"\']+)',
                    r'(C:\\[^\s<>"\']+)',
                    r'(/usr/[^\s<>"\']+)'
                ]
                
                for pattern in path_patterns:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        self.findings.append(BudgetFinding(
                            title="Internal Path Disclosure",
                            description=f"Error page reveals internal server paths: {matches[0]}",
                            recommendation="Configure custom error pages that don't reveal system paths",
                            proof_of_concept=f"GET {url} reveals path: {matches[0]}",
                            bounty_potential="$50-200",
                            category="information_disclosure"
                        ))
                        break
        except:
            pass
    
    def check_server_status_pages(self):
        """Check for exposed server status pages"""
        status_pages = [
            '/server-status', '/server-info', '/status', '/info.php',
            '/phpinfo.php', '/test.php', '/info', '/health', '/metrics'
        ]
        
        for page in status_pages:
            try:
                url = urllib.parse.urljoin(self.target_url, page)
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    status_indicators = [
                        'server status', 'apache status', 'nginx status',
                        'phpinfo', 'server information', 'system info'
                    ]
                    
                    if any(indicator in response.text.lower() for indicator in status_indicators):
                        self.findings.append(BudgetFinding(
                            title=f"Server Status Page Exposed - {page}",
                            description=f"Server status page {page} is publicly accessible",
                            recommendation="Restrict access to server status pages or disable them",
                            proof_of_concept=f"GET {url} returns server status information",
                            bounty_potential="$100-400",
                            category="information_disclosure"
                        ))
            except:
                continue
    
    def check_robots_txt_secrets(self):
        """Check robots.txt for interesting paths"""
        try:
            robots_url = urllib.parse.urljoin(self.target_url, '/robots.txt')
            response = self.session.get(robots_url, timeout=5)
            
            if response.status_code == 200:
                # Look for interesting disallowed paths
                interesting_paths = []
                lines = response.text.split('\n')
                
                for line in lines:
                    if line.strip().lower().startswith('disallow:'):
                        path = line.split(':', 1)[1].strip()
                        if any(keyword in path.lower() for keyword in [
                            'admin', 'config', 'backup', 'test', 'dev',
                            'private', 'secret', 'internal', 'api'
                        ]):
                            interesting_paths.append(path)
                
                if interesting_paths:
                    self.findings.append(BudgetFinding(
                        title="Sensitive Paths in robots.txt",
                        description=f"robots.txt reveals {len(interesting_paths)} potentially sensitive paths",
                        recommendation="Review robots.txt to ensure it doesn't reveal sensitive directories",
                        proof_of_concept=f"Interesting paths: {', '.join(interesting_paths[:3])}",
                        bounty_potential="$50-250",
                        category="information_disclosure"
                    ))
        except:
            pass
    
    def check_sitemap_information(self):
        """Check sitemap files for information disclosure"""
        sitemap_files = ['/sitemap.xml', '/sitemap.txt', '/sitemap_index.xml']
        
        for sitemap in sitemap_files:
            try:
                url = urllib.parse.urljoin(self.target_url, sitemap)
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    # Count URLs in sitemap
                    url_count = response.text.lower().count('<loc>') or response.text.count('http')
                    
                    if url_count > 100:  # Large sitemap
                        self.findings.append(BudgetFinding(
                            title=f"Large Sitemap Disclosure - {sitemap}",
                            description=f"Sitemap contains {url_count} URLs, potentially revealing site structure",
                            recommendation="Consider limiting sitemap size or using authentication",
                            proof_of_concept=f"GET {url} returns {url_count} URLs",
                            bounty_potential="$25-150",
                            category="information_disclosure"
                        ))
            except:
                continue
    
    def check_comments_disclosure(self):
        """Check for sensitive information in HTML comments"""
        try:
            response = self.session.get(self.target_url, timeout=10)
            
            # Extract HTML comments
            comment_pattern = r'<!--(.*?)-->'
            comments = re.findall(comment_pattern, response.text, re.DOTALL)
            
            sensitive_keywords = [
                'password', 'secret', 'key', 'token', 'api', 'admin',
                'todo', 'fixme', 'hack', 'temp', 'debug', 'test'
            ]
            
            for comment in comments:
                if any(keyword in comment.lower() for keyword in sensitive_keywords):
                    self.findings.append(BudgetFinding(
                        title="Sensitive Information in HTML Comments",
                        description="HTML comments contain potentially sensitive information",
                        recommendation="Remove sensitive information from HTML comments",
                        proof_of_concept=f"Comment contains: {comment[:100]}...",
                        bounty_potential="$50-300",
                        category="information_disclosure"
                    ))
                    break  # Only report once
        except:
            pass
    
    def check_error_pages(self):
        """Check for information disclosure in error pages"""
        error_triggers = [
            '/admin/login.php',
            '/wp-admin/',
            '/administrator/',
            '/phpmyadmin/',
            '/database/',
            '/.git/',
            '/.svn/',
            '/config.php'
        ]
        
        for trigger in error_triggers:
            try:
                url = urllib.parse.urljoin(self.target_url, trigger)
                response = self.session.get(url, timeout=5)
                
                # Look for detailed error messages
                error_indicators = [
                    'mysql', 'postgresql', 'oracle', 'sql server',
                    'stack trace', 'line number', 'file path',
                    'exception', 'error in', 'fatal error'
                ]
                
                if any(indicator in response.text.lower() for indicator in error_indicators):
                    self.findings.append(BudgetFinding(
                        title=f"Detailed Error Message - {trigger}",
                        description="Error page reveals detailed system information",
                        recommendation="Configure custom error pages with minimal information",
                        proof_of_concept=f"GET {url} returns detailed error information",
                        bounty_potential="$75-250",
                        category="information_disclosure"
                    ))
            except:
                continue
    
    def check_admin_panels(self):
        """Check for exposed admin panels"""
        admin_paths = [
            '/admin', '/administrator', '/wp-admin', '/admin.php',
            '/admin/', '/control', '/panel', '/dashboard',
            '/manage', '/backend', '/cpanel'
        ]
        
        for path in admin_paths:
            try:
                url = urllib.parse.urljoin(self.target_url, path)
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    admin_indicators = [
                        'login', 'username', 'password', 'admin panel',
                        'dashboard', 'control panel', 'administration'
                    ]
                    
                    if any(indicator in response.text.lower() for indicator in admin_indicators):
                        self.findings.append(BudgetFinding(
                            title=f"Admin Panel Accessible - {path}",
                            description=f"Admin panel at {path} is publicly accessible",
                            recommendation="Implement IP restrictions or additional authentication for admin panels",
                            proof_of_concept=f"GET {url} returns admin interface",
                            bounty_potential="$100-500",
                            category="access_control"
                        ))
            except:
                continue
    
    def check_test_files(self):
        """Check for test files that might contain sensitive information"""
        test_files = [
            'test.php', 'test.html', 'test.txt', 'debug.php',
            'info.php', 'phpinfo.php', 'test.jsp', 'test.asp'
        ]
        
        for test_file in test_files:
            try:
                url = urllib.parse.urljoin(self.target_url, test_file)
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200 and len(response.content) > 50:
                    self.findings.append(BudgetFinding(
                        title=f"Test File Exposed - {test_file}",
                        description=f"Test file {test_file} is publicly accessible",
                        recommendation="Remove test files from production environment",
                        proof_of_concept=f"GET {url} returns test content",
                        bounty_potential="$50-200",
                        category="information_disclosure"
                    ))
            except:
                continue
    
    def check_development_files(self):
        """Check for development files"""
        dev_files = [
            '.git/config', '.svn/entries', '.DS_Store',
            'package.json', 'composer.json', 'Gemfile',
            'requirements.txt', 'yarn.lock', 'package-lock.json'
        ]
        
        for dev_file in dev_files:
            try:
                url = urllib.parse.urljoin(self.target_url, dev_file)
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    self.findings.append(BudgetFinding(
                        title=f"Development File Exposed - {dev_file}",
                        description=f"Development file {dev_file} reveals project structure",
                        recommendation="Remove development files from production or restrict access",
                        proof_of_concept=f"GET {url} returns development information",
                        bounty_potential="$75-300",
                        category="information_disclosure"
                    ))
            except:
                continue

def generate_budget_report(findings: List[BudgetFinding]) -> Dict[str, Any]:
    """Generate a budget-friendly vulnerability report"""
    total_potential = 0
    severity_counts = {'low': 0, 'medium': 0, 'high': 0}
    
    for finding in findings:
        severity_counts[finding.severity] += 1
        
        # Estimate bounty potential (rough calculation)
        bounty_range = finding.bounty_potential.replace('$', '').split('-')
        if len(bounty_range) == 2:
            try:
                avg_bounty = (int(bounty_range[0]) + int(bounty_range[1])) / 2
                total_potential += avg_bounty
            except:
                pass
    
    return {
        'total_findings': len(findings),
        'severity_breakdown': severity_counts,
        'estimated_bounty_potential': f"${int(total_potential)}",
        'difficulty_level': 'Easy to Medium',
        'time_investment': 'Low',
        'findings': [f.__dict__ for f in findings]
    }
