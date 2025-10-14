import requests
import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime
import json
import re
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import html
import urllib.parse
from django.conf import settings

class SecurityScanner:
    def __init__(self, url, timeout=10):
        self.url = url
        self.parsed_url = urlparse(url)
        self.domain = self.parsed_url.netloc
        self.results = {}
        self.session = requests.Session()
        self.session.timeout = timeout
        self.session.headers.update({
            'User-Agent': 'ZtionSec Security Scanner 1.0'
        })
        
    def scan_all(self):
        """Perform comprehensive security scan"""
        try:
            ssl_results = self.check_ssl_certificate()
            header_results = self.check_security_headers()
            cms_results = self.detect_cms()
            perf_results = self.check_performance()
            
            # Merge all results
            self.results.update(ssl_results)
            self.results.update(header_results)
            self.results.update(cms_results)
            self.results.update(perf_results)
            
            # Calculate score and grade
            score, grade = self.calculate_security_score(self.results)
            self.results['security_score'] = score
            self.results['grade'] = grade
            
            return self.results
        except Exception as e:
            self.results['error'] = str(e)
            return self.results
    
    def check_ssl_certificate(self):
        """Check SSL certificate validity and details"""
        try:
            if self.parsed_url.scheme == 'https':
                # Test SSL connection with simple method first
                try:
                    response = self.session.get(self.url, verify=True, timeout=10)
                    ssl_valid = True
                    ssl_grade = 'A'  # Default good grade for valid SSL
                except requests.exceptions.SSLError:
                    ssl_valid = False
                    ssl_grade = 'F'
                except:
                    ssl_valid = False
                    ssl_grade = 'F'
                
                # Try to get detailed certificate info
                try:
                    cert_pem = ssl.get_server_certificate((self.domain, 443))
                    cert_der = ssl.PEM_cert_to_DER_cert(cert_pem)
                    cert = x509.load_der_x509_certificate(cert_der, default_backend())
                    
                    return {
                        'ssl_valid': ssl_valid,
                        'ssl_issuer': cert.issuer.rfc4514_string(),
                        'ssl_expiry': cert.not_valid_after,
                        'ssl_grade': ssl_grade
                    }
                except:
                    # Fallback to basic SSL check
                    return {
                        'ssl_valid': ssl_valid,
                        'ssl_issuer': 'Unknown',
                        'ssl_expiry': None,
                        'ssl_grade': ssl_grade
                    }
            else:
                return {
                    'ssl_valid': False,
                    'ssl_grade': 'F',
                    'ssl_issuer': '',
                    'ssl_expiry': None
                }
        except Exception as e:
            return {
                'ssl_valid': False,
                'ssl_grade': 'F',
                'ssl_issuer': '',
                'ssl_expiry': None,
                'ssl_error': str(e)
            }
    
    def check_security_headers(self):
        """Check HTTP security headers"""
        try:
            response = self.session.get(self.url)
            headers = response.headers
            
            return {
                'has_hsts': 'Strict-Transport-Security' in headers,
                'has_csp': 'Content-Security-Policy' in headers,
                'has_xframe': 'X-Frame-Options' in headers,
                'has_xss_protection': 'X-XSS-Protection' in headers,
                'has_content_type': 'X-Content-Type-Options' in headers
            }
        except Exception as e:
            return {
                'has_hsts': False,
                'has_csp': False,
                'has_xframe': False,
                'has_xss_protection': False,
                'has_content_type': False,
                'headers_error': str(e)
            }
    
    def _calculate_ssl_grade(self, cert):
        """Calculate SSL grade based on certificate"""
        # Simplified SSL grading
        try:
            # Check expiry
            days_until_expiry = (cert.not_valid_after - datetime.now()).days
            
            if days_until_expiry > 90:
                return 'A'
            elif days_until_expiry > 30:
                return 'B'
            elif days_until_expiry > 0:
                return 'C'
            else:
                return 'F'
        except Exception:
            return 'F'
    
    def check_ssl(self):
        """Check SSL certificate validity and details"""
        try:
            if self.parsed_url.scheme == 'https':
                context = ssl.create_default_context()
                with socket.create_connection((self.domain, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                        cert = ssock.getpeercert()
                        
                        self.results['ssl_valid'] = True
                        self.results['ssl_issuer'] = cert.get('issuer', [{}])[0].get('organizationName', 'Unknown')
                        
                        # Parse expiry date
                        expiry_str = cert.get('notAfter')
                        if expiry_str:
                            expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                            self.results['ssl_expiry'] = expiry_date
                            
                            # Calculate days until expiry
                            days_left = (expiry_date - datetime.now()).days
                            if days_left > 30:
                                self.results['ssl_grade'] = 'A'
                            elif days_left > 7:
                                self.results['ssl_grade'] = 'B'
                            else:
                                self.results['ssl_grade'] = 'C'
                        else:
                            self.results['ssl_grade'] = 'F'
            else:
                self.results['ssl_valid'] = False
                self.results['ssl_grade'] = 'F'
                
        except Exception as e:
            self.results['ssl_valid'] = False
            self.results['ssl_grade'] = 'F'
            self.results['ssl_error'] = str(e)
    
    def check_headers(self):
        """Check HTTP security headers"""
        try:
            response = requests.get(self.url, timeout=10, allow_redirects=True)
            headers = response.headers
            
            # Check security headers
            self.results['has_hsts'] = 'strict-transport-security' in headers
            self.results['has_csp'] = 'content-security-policy' in headers
            self.results['has_xframe'] = 'x-frame-options' in headers
            self.results['has_xss_protection'] = 'x-xss-protection' in headers
            self.results['has_content_type'] = 'x-content-type-options' in headers
            
            # Server information
            self.results['server_info'] = headers.get('server', 'Unknown')
            
            # Store response for further analysis
            self.response = response
            
        except Exception as e:
            self.results['headers_error'] = str(e)
    
    def detect_cms(self):
        """Detect CMS and technologies"""
        try:
            if hasattr(self, 'response'):
                content = self.response.text
                headers = self.response.headers
                
                cms_signatures = {
                    'WordPress': [
                        r'wp-content',
                        r'wp-includes',
                        r'wordpress',
                        r'wp-json'
                    ],
                    'Drupal': [
                        r'drupal',
                        r'sites/default',
                        r'misc/drupal.js'
                    ],
                    'Joomla': [
                        r'joomla',
                        r'administrator/index.php',
                        r'media/system/js'
                    ],
                    'Magento': [
                        r'magento',
                        r'skin/frontend',
                        r'js/mage'
                    ],
                    'Shopify': [
                        r'shopify',
                        r'cdn.shopify.com',
                        r'assets/shopify'
                    ]
                }
                
                detected_cms = []
                for cms, patterns in cms_signatures.items():
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            detected_cms.append(cms)
                            break
                
                self.results['cms_detected'] = ', '.join(detected_cms) if detected_cms else 'Unknown'
                
                # Try to detect version from generator meta tag
                soup = BeautifulSoup(content, 'html.parser')
                generator = soup.find('meta', {'name': 'generator'})
                if generator:
                    self.results['cms_version'] = generator.get('content', '')
                
        except Exception as e:
            self.results['cms_error'] = str(e)
    
    def check_performance(self):
        """Check response time and status"""
        try:
            start_time = time.time()
            response = requests.get(self.url, timeout=10)
            end_time = time.time()
            
            self.results['response_time'] = round((end_time - start_time) * 1000, 2)  # in milliseconds
            self.results['status_code'] = response.status_code
            
        except Exception as e:
            self.results['performance_error'] = str(e)
    
    def calculate_security_score(self, results=None):
        """Calculate overall security score with improved algorithm"""
        if results is None:
            results = self.results
            
        score = 0
        
        # Base score for successful scan
        if results.get('status_code') == 200:
            score += 10
        
        # SSL Score (35 points)
        if results.get('ssl_valid', False):
            ssl_grade = results.get('ssl_grade', 'F')
            if ssl_grade in ['A+']:
                score += 35
            elif ssl_grade in ['A']:
                score += 30
            elif ssl_grade in ['A-']:
                score += 25
            elif ssl_grade in ['B+']:
                score += 20
            elif ssl_grade in ['B']:
                score += 15
            elif ssl_grade in ['B-']:
                score += 10
            elif ssl_grade in ['C']:
                score += 5
        else:
            # Even if SSL is not valid, give some points for HTTPS attempt
            if self.url.startswith('https://'):
                score += 5
        
        # Security Headers (40 points - 8 each)
        headers_score = 0
        if results.get('has_hsts', False):
            headers_score += 8
        if results.get('has_csp', False):
            headers_score += 8
        if results.get('has_xframe', False):
            headers_score += 8
        if results.get('has_xss_protection', False):
            headers_score += 8
        if results.get('has_content_type', False):
            headers_score += 8
        
        score += headers_score
        
        # Performance (15 points)
        response_time = results.get('response_time', 10000)
        if response_time and response_time > 0:
            if response_time < 500:  # Very fast
                score += 15
            elif response_time < 1000:  # Fast
                score += 12
            elif response_time < 2000:  # Good
                score += 10
            elif response_time < 3000:  # Acceptable
                score += 8
            elif response_time < 5000:  # Slow
                score += 5
            elif response_time < 10000:  # Very slow
                score += 2
        
        # Ensure minimum score for working websites
        if score < 20 and results.get('status_code') == 200:
            score = 20
        
        # Assign grade
        if score >= 95:
            grade = 'A+'
        elif score >= 90:
            grade = 'A'
        elif score >= 85:
            grade = 'A-'
        elif score >= 80:
            grade = 'B+'
        elif score >= 75:
            grade = 'B'
        elif score >= 70:
            grade = 'B-'
        elif score >= 65:
            grade = 'C+'
        elif score >= 60:
            grade = 'C'
        elif score >= 55:
            grade = 'C-'
        elif score >= 50:
            grade = 'D'
        else:
            grade = 'F'
        
        return score, grade


class HaveIBeenPwnedChecker:
    def __init__(self):
        self.api_url = "https://haveibeenpwned.com/api/v3/breachedaccount/"
        
    def check_email(self, email):
        """Check if email was in any data breaches"""
        try:
            # Get API key from environment or settings
            api_key = getattr(settings, 'HAVEIBEENPWNED_API_KEY', None) or os.environ.get('HAVEIBEENPWNED_API_KEY')
            
            if not api_key:
                return {
                    'error': 'HaveIBeenPwned API key not configured. Please set HAVEIBEENPWNED_API_KEY in environment variables.'
                }
            
            headers = {
                'User-Agent': 'ZtionSec Security Scanner v1.0',
                'hibp-api-key': api_key
            }
            
            response = requests.get(f"{self.api_url}{email}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                breaches = response.json()
                return {
                    'breaches_found': len(breaches),
                    'breach_details': [breach['Name'] for breach in breaches]
                }
            elif response.status_code == 404:
                return {
                    'breaches_found': 0,
                    'breach_details': []
                }
            else:
                return {
                    'error': f"API returned status code: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'breaches_found': 0,
                'breach_details': [],
                'error': str(e)
            }
    
    def format_breach_data(self, raw_breach):
        """Format breach data for consistent output"""
        return {
            'name': raw_breach.get('Name', ''),
            'date': raw_breach.get('BreachDate', ''),
            'description': raw_breach.get('Description', ''),
            'data_classes': raw_breach.get('DataClasses', [])
        }


# Additional utility functions for testing
def validate_url(url):
    """Validate URL format and protocol"""
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        return parsed.scheme in ['http', 'https'] and parsed.netloc
    except Exception:
        return False


def extract_domain(url):
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.split(':')[0]  # Remove port if present
    except Exception:
        return ''


def calculate_grade(score):
    """Calculate letter grade from numeric score"""
    if score >= 95:
        return 'A+'
    elif score >= 90:
        return 'A'
    elif score >= 85:
        return 'A-'
    elif score >= 80:
        return 'B+'
    elif score >= 75:
        return 'B'
    elif score >= 70:
        return 'B-'
    elif score >= 65:
        return 'C+'
    elif score >= 60:
        return 'C'
    elif score >= 55:
        return 'C-'
    elif score >= 50:
        return 'D'
    else:
        return 'F'


def sanitize_input(input_string):
    """Sanitize user input to prevent XSS and injection attacks"""
    if not input_string:
        return input_string
    
    # HTML escape
    sanitized = html.escape(input_string)
    
    # Remove potentially dangerous SQL keywords
    dangerous_patterns = [
        'DROP TABLE', 'DELETE FROM', 'INSERT INTO', 'UPDATE SET',
        'UNION SELECT', 'OR 1=1', 'AND 1=1', '--', ';'
    ]
    
    for pattern in dangerous_patterns:
        sanitized = sanitized.replace(pattern.upper(), '')
        sanitized = sanitized.replace(pattern.lower(), '')
    
    # URL encode for safety
    sanitized = urllib.parse.quote_plus(sanitized, safe='/:?#[]@!$&\'()*+,;=')
    
    return sanitized
