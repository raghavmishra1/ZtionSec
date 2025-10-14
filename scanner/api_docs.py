"""
API Documentation for ZtionSec
Senior Developer Implementation - Swagger/OpenAPI Integration
"""

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# API Schema Definition
schema_view = get_schema_view(
    openapi.Info(
        title="ZtionSec Security Analysis API",
        default_version='v1',
        description="""
        # ZtionSec Security Analysis Platform API

        ## Overview
        The ZtionSec API provides comprehensive security analysis capabilities for websites and email breach checking.
        This RESTful API allows you to integrate security scanning into your applications and workflows.

        ## Authentication
        Currently, the API uses session-based authentication. API key authentication will be added in future versions.

        ## Rate Limiting
        - **Scan Endpoints**: 10 requests per hour per IP
        - **API Endpoints**: 100 requests per hour per IP
        - **Breach Check**: 5 requests per hour per IP

        ## Response Format
        All responses are in JSON format with consistent error handling:

        ```json
        {
            "success": true,
            "data": {...},
            "message": "Operation completed successfully"
        }
        ```

        ## Error Codes
        - **400**: Bad Request - Invalid parameters
        - **401**: Unauthorized - Authentication required
        - **403**: Forbidden - Insufficient permissions
        - **429**: Too Many Requests - Rate limit exceeded
        - **500**: Internal Server Error - Server error

        ## Security Features Analyzed
        - SSL/TLS Certificate Analysis
        - HTTP Security Headers
        - CMS Detection and Versioning
        - Performance Metrics
        - Vulnerability Assessment
        - Data Breach History
        """,
        terms_of_service="https://ztionsec.com/terms/",
        contact=openapi.Contact(email="api@ztionsec.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# API Response Schemas
security_scan_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Request success status'),
        'data': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'url': openapi.Schema(type=openapi.TYPE_STRING, description='Scanned URL'),
                'ssl_valid': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='SSL certificate validity'),
                'ssl_grade': openapi.Schema(type=openapi.TYPE_STRING, description='SSL security grade (A+ to F)'),
                'ssl_issuer': openapi.Schema(type=openapi.TYPE_STRING, description='SSL certificate issuer'),
                'ssl_expiry': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='SSL expiry date'),
                'has_hsts': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='HSTS header present'),
                'has_csp': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='CSP header present'),
                'has_xframe': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='X-Frame-Options header present'),
                'has_xss_protection': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='X-XSS-Protection header present'),
                'has_content_type': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='X-Content-Type-Options header present'),
                'cms_detected': openapi.Schema(type=openapi.TYPE_STRING, description='Detected CMS'),
                'cms_version': openapi.Schema(type=openapi.TYPE_STRING, description='CMS version'),
                'response_time': openapi.Schema(type=openapi.TYPE_NUMBER, description='Response time in milliseconds'),
                'status_code': openapi.Schema(type=openapi.TYPE_INTEGER, description='HTTP status code'),
                'security_score': openapi.Schema(type=openapi.TYPE_INTEGER, description='Overall security score (0-100)'),
                'grade': openapi.Schema(type=openapi.TYPE_STRING, description='Security grade (A+ to F)'),
                'server_info': openapi.Schema(type=openapi.TYPE_STRING, description='Server information'),
            }
        ),
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Response message'),
    }
)

breach_check_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Request success status'),
        'data': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Checked email address'),
                'breaches_found': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of breaches found'),
                'breach_details': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Breach name'),
                            'date': openapi.Schema(type=openapi.TYPE_STRING, description='Breach date'),
                            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Breach description'),
                            'data_classes': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_STRING),
                                description='Types of data compromised'
                            ),
                        }
                    ),
                    description='Detailed breach information'
                ),
            }
        ),
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Response message'),
    }
)

error_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Request success status (false)'),
        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
        'code': openapi.Schema(type=openapi.TYPE_STRING, description='Error code'),
    }
)

# Request Schemas
scan_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['url'],
    properties={
        'url': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='URL to scan (must include protocol)',
            example='https://example.com'
        ),
        'scan_type': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Type of scan to perform',
            enum=['basic', 'comprehensive', 'quick'],
            default='basic'
        ),
    }
)

breach_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email'],
    properties={
        'email': openapi.Schema(
            type=openapi.TYPE_STRING,
            format='email',
            description='Email address to check for breaches',
            example='user@example.com'
        ),
    }
)

# API Documentation Decorators
def api_scan_docs():
    """Decorator for scan API documentation"""
    return {
        'operation_description': """
        Perform a comprehensive security scan of a website.
        
        This endpoint analyzes:
        - SSL/TLS certificate configuration
        - HTTP security headers
        - CMS detection and versioning
        - Performance metrics
        - Overall security scoring
        
        **Rate Limit**: 10 requests per hour per IP address
        """,
        'request_body': scan_request_schema,
        'responses': {
            200: openapi.Response('Scan completed successfully', security_scan_response_schema),
            400: openapi.Response('Invalid request parameters', error_response_schema),
            429: openapi.Response('Rate limit exceeded', error_response_schema),
            500: openapi.Response('Internal server error', error_response_schema),
        },
        'tags': ['Security Scanning'],
    }

def api_breach_docs():
    """Decorator for breach check API documentation"""
    return {
        'operation_description': """
        Check if an email address has been involved in any known data breaches.
        
        This endpoint uses the HaveIBeenPwned database to check for:
        - Known data breaches
        - Breach dates and details
        - Types of data compromised
        - Security recommendations
        
        **Rate Limit**: 5 requests per hour per IP address
        """,
        'request_body': breach_request_schema,
        'responses': {
            200: openapi.Response('Breach check completed', breach_check_response_schema),
            400: openapi.Response('Invalid email address', error_response_schema),
            429: openapi.Response('Rate limit exceeded', error_response_schema),
            500: openapi.Response('Internal server error', error_response_schema),
        },
        'tags': ['Breach Checking'],
    }

# API Examples
API_EXAMPLES = {
    'scan_request': {
        "url": "https://example.com",
        "scan_type": "comprehensive"
    },
    'scan_response': {
        "success": True,
        "data": {
            "url": "https://example.com",
            "ssl_valid": True,
            "ssl_grade": "A",
            "ssl_issuer": "Let's Encrypt",
            "ssl_expiry": "2024-12-31T23:59:59Z",
            "has_hsts": True,
            "has_csp": False,
            "has_xframe": True,
            "has_xss_protection": True,
            "has_content_type": True,
            "cms_detected": "WordPress",
            "cms_version": "6.2",
            "response_time": 245.67,
            "status_code": 200,
            "security_score": 85,
            "grade": "A",
            "server_info": "nginx/1.18.0"
        },
        "message": "Security scan completed successfully"
    },
    'breach_request': {
        "email": "user@example.com"
    },
    'breach_response': {
        "success": True,
        "data": {
            "email": "user@example.com",
            "breaches_found": 2,
            "breach_details": [
                {
                    "name": "Adobe",
                    "date": "2013-10-04",
                    "description": "Adobe breach description",
                    "data_classes": ["Email addresses", "Passwords"]
                },
                {
                    "name": "LinkedIn",
                    "date": "2012-05-05",
                    "description": "LinkedIn breach description",
                    "data_classes": ["Email addresses", "Passwords"]
                }
            ]
        },
        "message": "Breach check completed successfully"
    }
}
