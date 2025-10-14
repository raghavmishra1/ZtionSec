"""
Production settings for ZtionSec
Enhanced security configuration for production deployment
"""

import os
from pathlib import Path
from .settings import *

# Load environment variables
def get_env_variable(var_name, default=None):
    """Get environment variable or return default"""
    return os.environ.get(var_name, default)

# Security Settings
SECRET_KEY = get_env_variable('SECRET_KEY', SECRET_KEY)
DEBUG = get_env_variable('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = get_env_variable('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database Configuration
DATABASE_URL = get_env_variable('DATABASE_URL', 'sqlite:///db.sqlite3')
if DATABASE_URL.startswith('postgresql://'):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }

# API Keys Configuration
HAVEIBEENPWNED_API_KEY = get_env_variable('HAVEIBEENPWNED_API_KEY')
SHODAN_API_KEY = get_env_variable('SHODAN_API_KEY')
CENSYS_API_ID = get_env_variable('CENSYS_API_ID')
CENSYS_API_SECRET = get_env_variable('CENSYS_API_SECRET')

# Enhanced Security Settings
if not DEBUG:
    # Force HTTPS in production
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Session Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_AGE = int(get_env_variable('SESSION_COOKIE_AGE', '3600'))
    
    # CSRF Security
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Strict'
    CSRF_COOKIE_AGE = int(get_env_variable('CSRF_COOKIE_AGE', '3600'))
    
    # HSTS Settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Additional Security Headers
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    X_FRAME_OPTIONS = 'DENY'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = get_env_variable('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(get_env_variable('EMAIL_PORT', '25'))
EMAIL_USE_TLS = get_env_variable('EMAIL_USE_TLS', 'False').lower() == 'true'
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD', '')

# Redis Configuration (if available)
REDIS_URL = get_env_variable('REDIS_URL')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# Rate Limiting Configuration
RATE_LIMIT_ENABLED = get_env_variable('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
SCAN_RATE_LIMIT = get_env_variable('SCAN_RATE_LIMIT', '10/hour')
API_RATE_LIMIT = get_env_variable('API_RATE_LIMIT', '100/hour')

# Enhanced Logging Configuration
LOG_LEVEL = get_env_variable('LOG_LEVEL', 'INFO')
SECURITY_LOG_LEVEL = get_env_variable('SECURITY_LOG_LEVEL', 'WARNING')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'security': {
            'format': '[SECURITY] {levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'ztionsec.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': SECURITY_LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'security',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'security': {
            'handlers': ['security_file', 'console'],
            'level': SECURITY_LOG_LEVEL,
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': SECURITY_LOG_LEVEL,
            'propagate': False,
        },
        'scanner': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# Static Files Configuration for Production
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media Files Configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Create necessary directories
import os
for directory in [BASE_DIR / 'logs', BASE_DIR / 'staticfiles', BASE_DIR / 'media']:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
