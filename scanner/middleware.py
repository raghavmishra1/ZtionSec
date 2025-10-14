"""
Security Middleware for ZtionSec
Adds comprehensive security headers to all responses
"""

class SecurityHeadersMiddleware:
    """
    Middleware to add comprehensive security headers to all responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy (CSP) - Development-friendly policy
        from django.conf import settings
        import os
        
        # Check if CSP should be disabled for development
        disable_csp = os.environ.get('DISABLE_CSP', 'false').lower() == 'true'
        
        if not disable_csp:
            if settings.DEBUG:
                # Development CSP with full AdSense support
                csp_policy = (
                    "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: * https:; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: * https:; "
                    "style-src 'self' 'unsafe-inline' data: blob: * https:; "
                    "img-src 'self' data: blob: * https:; "
                    "font-src 'self' data: blob: * https:; "
                    "connect-src 'self' data: blob: * ws: wss: https:; "
                    "frame-src 'self' * https:; "
                    "object-src 'self' * https:; "
                    "base-uri 'self'; "
                    "form-action 'self'; "
                    "frame-ancestors 'self'"
                )
                response['Content-Security-Policy'] = csp_policy
            else:
                # Production CSP with comprehensive AdSense support
                csp_policy = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://pagead2.googlesyndication.com https://www.googletagmanager.com https://www.google.com https://googleads.g.doubleclick.net https://partner.googleadservices.com https://tpc.googlesyndication.com; "
                    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
                    "img-src 'self' data: https: blob: https://pagead2.googlesyndication.com https://www.google.com https://googleads.g.doubleclick.net https://partner.googleadservices.com https://tpc.googlesyndication.com; "
                    "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
                    "connect-src 'self' https://pagead2.googlesyndication.com https://www.google.com https://googleads.g.doubleclick.net https://partner.googleadservices.com; "
                    "frame-src 'self' https://googleads.g.doubleclick.net https://www.google.com https://partner.googleadservices.com https://tpc.googlesyndication.com; "
                    "object-src 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self'; "
                    "frame-ancestors 'none'; "
                    "upgrade-insecure-requests"
                )
                response['Content-Security-Policy'] = csp_policy
        
        # Strict Transport Security (HSTS) - Force HTTPS
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # X-Frame-Options - Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # X-Content-Type-Options - Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-XSS-Protection - Enable XSS filtering
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy - Control referrer information
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy - Control browser features
        permissions_policy = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "speaker=(), "
            "vibrate=(), "
            "fullscreen=(self), "
            "payment=()"
        )
        response['Permissions-Policy'] = permissions_policy
        
        # Cross-Origin Embedder Policy
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        
        # Cross-Origin Opener Policy
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        
        # Cross-Origin Resource Policy
        response['Cross-Origin-Resource-Policy'] = 'same-origin'
        
        # Cache Control for sensitive pages
        if request.path.startswith('/advanced/') or request.path.startswith('/admin/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        # Server header removal and replacement (security through obscurity)
        if 'Server' in response:
            del response['Server']
        response['Server'] = 'ZtionSec/1.0'  # Generic server identifier
        
        # X-Powered-By header removal
        if 'X-Powered-By' in response:
            del response['X-Powered-By']
        
        # Remove Django version information
        if 'X-Django-Version' in response:
            del response['X-Django-Version']
            
        return response


class PathSecurityMiddleware:
    """
    Middleware to handle security for sensitive paths and prevent information disclosure
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Paths that should return 404 instead of revealing system information
        self.blocked_paths = [
            '/wp-admin/', '/wp-admin', '/wp-login.php', '/wp-config.php',
            '/administrator/', '/administrator', '/admin.php',
            '/phpmyadmin/', '/phpmyadmin', '/pma/', '/mysql/',
            '/database/', '/database', '/db/', '/sql/',
            '/.git/', '/.git', '/.svn/', '/.svn',
            '/config.php', '/config/', '/configuration.php',
            '/.env', '/.htaccess', '/web.config',
            '/backup/', '/backups/', '/dump/', '/dumps/',
            '/test/', '/testing/', '/dev/', '/development/',
            '/staging/', '/temp/', '/tmp/',
            '/phpinfo.php', '/info.php', '/test.php',
            '/readme.txt', '/readme.html', '/license.txt',
            '/robots.txt', '/sitemap.xml'  # These can stay but we'll monitor
        ]
        
        # Admin paths that need authentication
        self.admin_paths = ['/admin/', '/admin']

    def __call__(self, request):
        # Check for blocked paths first
        path = request.path.lower()
        
        # Block common attack paths
        for blocked_path in self.blocked_paths:
            if path.startswith(blocked_path.lower()) or path == blocked_path.lower():
                # Don't reveal that these paths don't exist - just return 404
                from django.http import Http404
                raise Http404("Page not found")
        
        # Handle admin panel access
        if any(path.startswith(admin_path) for admin_path in self.admin_paths):
            # Check if user is authenticated and is staff
            if not request.user.is_authenticated or not request.user.is_staff:
                # Log unauthorized admin access attempt
                import logging
                security_logger = logging.getLogger('security')
                security_logger.warning(
                    f"Unauthorized admin access attempt: {request.method} {request.path} "
                    f"from {request.META.get('REMOTE_ADDR', 'unknown')} "
                    f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'unknown')}"
                )
                
                # Return 404 instead of revealing admin panel exists
                from django.http import Http404
                raise Http404("Page not found")
        
        response = self.get_response(request)
        
        # Additional security for error responses
        if response.status_code >= 400:
            # Remove detailed error information in production
            from django.conf import settings
            if not settings.DEBUG:
                # Replace detailed error pages with generic ones
                if response.status_code == 500:
                    from django.http import HttpResponse
                    response = HttpResponse(
                        "Internal Server Error", 
                        status=500,
                        content_type='text/plain'
                    )
                elif response.status_code == 404:
                    from django.http import HttpResponse
                    response = HttpResponse(
                        "Page Not Found", 
                        status=404,
                        content_type='text/plain'
                    )
        
        return response


class HTTPSRedirectMiddleware:
    """
    Middleware to redirect HTTP requests to HTTPS in production
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if request is not secure and not in debug mode
        from django.conf import settings
        
        if not request.is_secure() and not settings.DEBUG:
            # Build HTTPS URL
            https_url = request.build_absolute_uri().replace('http://', 'https://')
            
            from django.http import HttpResponsePermanentRedirect
            return HttpResponsePermanentRedirect(https_url)
        
        return self.get_response(request)


class SecurityAuditMiddleware:
    """
    Middleware to log security-related events for auditing
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import logging
        
        # Log potential security issues
        security_logger = logging.getLogger('security')
        
        # Check for suspicious patterns
        suspicious_patterns = [
            'script>', '<iframe', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
            '../', '..\\', '/etc/passwd', '/proc/', 'cmd.exe', 'powershell'
        ]
        
        # Check URL and parameters for suspicious content
        full_path = request.get_full_path().lower()
        for pattern in suspicious_patterns:
            if pattern in full_path:
                security_logger.warning(
                    f"Suspicious request detected: {request.method} {request.get_full_path()} "
                    f"from {request.META.get('REMOTE_ADDR', 'unknown')} "
                    f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'unknown')}"
                )
                break
        
        # Check POST data for suspicious content
        if request.method == 'POST':
            try:
                post_data = str(request.POST).lower()
                for pattern in suspicious_patterns:
                    if pattern in post_data:
                        security_logger.warning(
                            f"Suspicious POST data detected from {request.META.get('REMOTE_ADDR', 'unknown')}"
                        )
                        break
            except:
                pass  # Ignore errors in security logging
        
        response = self.get_response(request)
        
        # Log failed authentication attempts
        if response.status_code == 403:
            security_logger.warning(
                f"403 Forbidden: {request.method} {request.get_full_path()} "
                f"from {request.META.get('REMOTE_ADDR', 'unknown')}"
            )
        
        return response
