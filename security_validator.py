#!/usr/bin/env python3
"""
ZtionSec Security Validation Script
Checks for common security misconfigurations
"""

import os
import sys
import django
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ztionsec.settings')
django.setup()

from django.conf import settings

class SecurityValidator:
    def __init__(self):
        self.issues = []
        self.warnings = []
        
    def check_debug_mode(self):
        """Check if DEBUG is disabled in production"""
        if settings.DEBUG:
            self.issues.append("🔴 CRITICAL: DEBUG=True in production exposes sensitive information")
        else:
            print("✅ DEBUG mode is properly disabled")
    
    def check_secret_key(self):
        """Check SECRET_KEY security"""
        if not settings.SECRET_KEY:
            self.issues.append("🔴 CRITICAL: SECRET_KEY is empty")
        elif len(settings.SECRET_KEY) < 50:
            self.issues.append("🔴 CRITICAL: SECRET_KEY is too short (< 50 characters)")
        elif 'ztionsec-prod-key-2024' in settings.SECRET_KEY:
            self.issues.append("🔴 CRITICAL: Using default/predictable SECRET_KEY")
        else:
            print("✅ SECRET_KEY appears to be secure")
    
    def check_allowed_hosts(self):
        """Check ALLOWED_HOSTS configuration"""
        if '*' in settings.ALLOWED_HOSTS:
            self.issues.append("🔴 CRITICAL: ALLOWED_HOSTS contains wildcard '*' - vulnerable to Host Header attacks")
        elif not settings.ALLOWED_HOSTS:
            self.issues.append("🔴 CRITICAL: ALLOWED_HOSTS is empty")
        else:
            print("✅ ALLOWED_HOSTS is properly configured")
    
    def check_https_settings(self):
        """Check HTTPS/SSL configuration"""
        if not settings.DEBUG:
            if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
                self.warnings.append("🟡 WARNING: SECURE_SSL_REDIRECT not enabled")
            if not getattr(settings, 'SECURE_HSTS_SECONDS', 0):
                self.warnings.append("🟡 WARNING: HSTS not configured")
            if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
                self.warnings.append("🟡 WARNING: SESSION_COOKIE_SECURE not enabled")
            if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
                self.warnings.append("🟡 WARNING: CSRF_COOKIE_SECURE not enabled")
        
        if all([
            getattr(settings, 'SECURE_SSL_REDIRECT', False),
            getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0,
            getattr(settings, 'SESSION_COOKIE_SECURE', False),
            getattr(settings, 'CSRF_COOKIE_SECURE', False)
        ]):
            print("✅ HTTPS/SSL settings are properly configured")
    
    def check_admin_security(self):
        """Check admin panel security"""
        admin_url = getattr(settings, 'ADMIN_URL_PATH', 'admin')
        if admin_url == 'admin':
            self.warnings.append("🟡 WARNING: Using default admin URL - consider changing for security")
        else:
            print("✅ Admin URL is customized for security")
    
    def check_database_security(self):
        """Check database configuration"""
        db_config = settings.DATABASES.get('default', {})
        if db_config.get('ENGINE') == 'django.db.backends.sqlite3':
            if not settings.DEBUG:
                self.warnings.append("🟡 WARNING: Using SQLite in production - consider PostgreSQL")
        print("✅ Database configuration checked")
    
    def check_middleware_security(self):
        """Check security middleware configuration"""
        required_middleware = [
            'scanner.middleware.SecurityHeadersMiddleware',
            'scanner.middleware.SecurityAuditMiddleware',
            'django.middleware.security.SecurityMiddleware',
        ]
        
        missing_middleware = []
        for middleware in required_middleware:
            if middleware not in settings.MIDDLEWARE:
                missing_middleware.append(middleware)
        
        if missing_middleware:
            self.warnings.append(f"🟡 WARNING: Missing security middleware: {', '.join(missing_middleware)}")
        else:
            print("✅ Security middleware is properly configured")
    
    def run_validation(self):
        """Run all security checks"""
        print("🔍 Running ZtionSec Security Validation...\n")
        
        self.check_debug_mode()
        self.check_secret_key()
        self.check_allowed_hosts()
        self.check_https_settings()
        self.check_admin_security()
        self.check_database_security()
        self.check_middleware_security()
        
        print("\n" + "="*60)
        print("🛡️  SECURITY VALIDATION REPORT")
        print("="*60)
        
        if self.issues:
            print("\n🔴 CRITICAL ISSUES FOUND:")
            for issue in self.issues:
                print(f"  {issue}")
        
        if self.warnings:
            print("\n🟡 WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.issues and not self.warnings:
            print("\n🎉 ALL SECURITY CHECKS PASSED!")
            print("✅ Your ZtionSec platform appears to be securely configured.")
        
        print(f"\n📊 Summary: {len(self.issues)} critical issues, {len(self.warnings)} warnings")
        
        if self.issues:
            print("\n⚠️  Please fix critical issues before deploying to production!")
            return False
        
        return True

if __name__ == "__main__":
    validator = SecurityValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)
