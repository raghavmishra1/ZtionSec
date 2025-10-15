"""
Production deployment settings for ZtionSec
Optimized for free hosting platforms like Render, Railway, and Heroku
"""

import os
import dj_database_url
from decouple import config
from .settings import *

# Add REST framework and CORS to installed apps
INSTALLED_APPS += [
    'rest_framework',
    'corsheaders',
]

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# CORS settings for frontend
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend.netlify.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Override settings for production deployment
DEBUG = config('DEBUG', default=False, cast=bool)

# Security settings
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here-change-in-production')

# Allowed hosts
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

# Database configuration with connection pooling
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(
            os.environ.get('DATABASE_URL'),
            conn_max_age=600,  # Connection pooling for 10 minutes
        )
    }
    # Additional database optimization for cold start prevention
    DATABASES['default'].update({
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
        'OPTIONS': {
            'MAX_CONNS': 20,  # Maximum number of connections
            'MIN_CONNS': 2,   # Minimum number of connections to maintain
        }
    })
else:
    # Fallback to SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'CONN_MAX_AGE': 300,  # Connection pooling for SQLite too
        }
    }

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Whitenoise for static file serving
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Force HTTPS in production
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# API Keys (optional - set in environment variables)
HAVEIBEENPWNED_API_KEY = config('HAVEIBEENPWNED_API_KEY', default='')
SHODAN_API_KEY = config('SHODAN_API_KEY', default='')
CENSYS_API_ID = config('CENSYS_API_ID', default='')
CENSYS_API_SECRET = config('CENSYS_API_SECRET', default='')

# Disable some resource-intensive features for free hosting
ENABLE_ADVANCED_SCANNING = config('ENABLE_ADVANCED_SCANNING', default=True, cast=bool)
ENABLE_PORT_SCANNING = config('ENABLE_PORT_SCANNING', default=False, cast=bool)  # Disabled for free hosting
ENABLE_VULNERABILITY_SCANNING = config('ENABLE_VULNERABILITY_SCANNING', default=True, cast=bool)

# Rate limiting for free hosting
RATE_LIMIT_SCANS_PER_HOUR = config('RATE_LIMIT_SCANS_PER_HOUR', default=5, cast=int)
RATE_LIMIT_API_CALLS_PER_HOUR = config('RATE_LIMIT_API_CALLS_PER_HOUR', default=50, cast=int)
