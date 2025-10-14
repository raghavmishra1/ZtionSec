"""
Rate limiting middleware for ZtionSec
Provides protection against abuse and DoS attacks
"""

import time
import hashlib
from collections import defaultdict
from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings
import logging

security_logger = logging.getLogger('security')

class RateLimitMiddleware:
    """
    Rate limiting middleware to prevent abuse
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limits = {
            'scan': {'limit': 10, 'period': 3600},  # 10 scans per hour
            'api': {'limit': 100, 'period': 3600},   # 100 API calls per hour
            'breach': {'limit': 20, 'period': 3600}, # 20 breach checks per hour
            'default': {'limit': 200, 'period': 3600} # 200 requests per hour
        }
        
    def __call__(self, request):
        # Skip rate limiting if disabled
        if not getattr(settings, 'RATE_LIMIT_ENABLED', True):
            return self.get_response(request)
            
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Skip rate limiting for Render health checks and other exempt sources
        if self.is_exempt_from_rate_limiting(request, client_ip):
            return self.get_response(request)
        
        # Determine rate limit type based on path
        rate_limit_type = self.get_rate_limit_type(request.path)
        
        # Check rate limit
        if self.is_rate_limited(client_ip, rate_limit_type):
            security_logger.warning(f"Rate limit exceeded for IP {client_ip} on {request.path}")
            return HttpResponse(
                "Rate limit exceeded. Please try again later.",
                status=429,
                content_type='text/plain'
            )
        
        # Record the request
        self.record_request(client_ip, rate_limit_type)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_exempt_from_rate_limiting(self, request, client_ip):
        """Check if request should be exempt from rate limiting"""
        # Render health check IPs and patterns
        render_ips = [
            '10.228.25.145',  # Render health check IP from logs
            '127.0.0.1',      # Localhost
            '::1',            # IPv6 localhost
        ]
        
        # Render health check user agents
        exempt_user_agents = [
            'Render/1.0',           # Render health checks
            'Mediapartners-Google', # Google AdSense crawler
            'GoogleBot',            # Google crawler
            'bingbot',              # Bing crawler
            'facebookexternalhit',  # Facebook crawler
            'Twitterbot',           # Twitter crawler
        ]
        
        # Check if IP is exempt
        if client_ip in render_ips:
            return True
        
        # Check if IP is in Render's IP range (10.x.x.x for internal services)
        if client_ip and client_ip.startswith('10.'):
            return True
        
        # Check user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        for exempt_agent in exempt_user_agents:
            if exempt_agent in user_agent:
                return True
        
        # Check if it's a health check endpoint
        if request.path in ['/api/v1/health/', '/health/', '/ping/', '/status/']:
            return True
        
        return False
    
    def get_rate_limit_type(self, path):
        """Determine rate limit type based on request path"""
        if '/scan' in path:
            return 'scan'
        elif '/api/' in path:
            return 'api'
        elif '/breach' in path:
            return 'breach'
        else:
            return 'default'
    
    def is_rate_limited(self, client_ip, rate_limit_type):
        """Check if client has exceeded rate limit"""
        config = self.rate_limits.get(rate_limit_type, self.rate_limits['default'])
        cache_key = f"rate_limit:{rate_limit_type}:{client_ip}"
        
        current_time = int(time.time())
        window_start = current_time - config['period']
        
        # Get request timestamps from cache with error handling
        try:
            requests = cache.get(cache_key, [])
        except Exception as e:
            # If cache fails, allow request but log error
            print(f"Cache error in rate limiting: {e}")
            return False
        
        # Filter out old requests
        requests = [req_time for req_time in requests if req_time > window_start]
        
        # Check if limit exceeded
        return len(requests) >= config['limit']
    
    def record_request(self, client_ip, rate_limit_type):
        """Record a request for rate limiting"""
        config = self.rate_limits.get(rate_limit_type, self.rate_limits['default'])
        cache_key = f"rate_limit:{rate_limit_type}:{client_ip}"
        
        current_time = int(time.time())
        window_start = current_time - config['period']
        
        # Get existing requests with error handling
        try:
            requests = cache.get(cache_key, [])
            
            # Filter out old requests and add new one
            requests = [req_time for req_time in requests if req_time > window_start]
            requests.append(current_time)
            
            # Store back in cache
            cache.set(cache_key, requests, config['period'])
        except Exception as e:
            # If cache fails, just log error and continue
            print(f"Cache error in record_request: {e}")


class SecurityMonitoringMiddleware:
    """
    Security monitoring middleware to detect suspicious activity
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_patterns = [
            r'\.\./', r'<script', r'javascript:', r'vbscript:',
            r'onload=', r'onerror=', r'onclick=', r'union.*select',
            r'drop.*table', r'insert.*into', r'delete.*from',
            r'exec\(', r'eval\(', r'system\(', r'passthru\(',
            r'shell_exec', r'file_get_contents', r'fopen\(',
            r'curl_exec', r'wget', r'nc\s', r'netcat'
        ]
        
    def __call__(self, request):
        # Monitor for suspicious activity
        self.check_suspicious_activity(request)
        
        response = self.get_response(request)
        return response
    
    def check_suspicious_activity(self, request):
        """Check for suspicious patterns in request"""
        import re
        
        client_ip = self.get_client_ip(request)
        suspicious_found = []
        
        # Check URL path
        for pattern in self.suspicious_patterns:
            if re.search(pattern, request.path, re.IGNORECASE):
                suspicious_found.append(f"URL: {pattern}")
        
        # Check query parameters
        for key, value in request.GET.items():
            for pattern in self.suspicious_patterns:
                if re.search(pattern, str(value), re.IGNORECASE):
                    suspicious_found.append(f"GET {key}: {pattern}")
        
        # Check POST data
        if request.method == 'POST':
            for key, value in request.POST.items():
                for pattern in self.suspicious_patterns:
                    if re.search(pattern, str(value), re.IGNORECASE):
                        suspicious_found.append(f"POST {key}: {pattern}")
        
        # Log suspicious activity
        if suspicious_found:
            security_logger.warning(
                f"Suspicious activity detected from IP {client_ip} on {request.path}: "
                f"{', '.join(suspicious_found)}"
            )
    
    def get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
