#!/usr/bin/env python3
"""
ZtionSec Production Deployment Script
Automates production setup and security hardening
"""

import os
import sys
import subprocess
import secrets
import string
from pathlib import Path

def generate_secret_key():
    """Generate a secure Django secret key"""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for i in range(50))

def create_env_file():
    """Create .env file with secure defaults"""
    env_path = Path('.env')
    
    if env_path.exists():
        print("⚠️  .env file already exists. Backing up to .env.backup")
        subprocess.run(['cp', '.env', '.env.backup'])
    
    secret_key = generate_secret_key()
    
    env_content = f"""# ZtionSec Production Environment Configuration
# Generated automatically - customize as needed

# Django Settings
SECRET_KEY={secret_key}
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# Security API Keys (Get these from respective services)
HAVEIBEENPWNED_API_KEY=your-hibp-api-key-here
SHODAN_API_KEY=your-shodan-api-key-here
CENSYS_API_ID=your-censys-api-id-here
CENSYS_API_SECRET=your-censys-api-secret-here

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_AGE=3600
CSRF_COOKIE_AGE=3600

# Rate Limiting
RATE_LIMIT_ENABLED=True
SCAN_RATE_LIMIT=10/hour
API_RATE_LIMIT=100/hour

# Logging
LOG_LEVEL=INFO
SECURITY_LOG_LEVEL=WARNING
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with secure defaults")
    return True

def setup_directories():
    """Create necessary directories"""
    directories = ['logs', 'staticfiles', 'media', 'ssl']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    return True

def install_production_dependencies():
    """Install additional production dependencies"""
    production_packages = [
        'gunicorn',  # WSGI server
        'whitenoise',  # Static file serving
        'python-dotenv',  # Environment variable loading
        'psycopg2-binary',  # PostgreSQL adapter
        'redis',  # Redis client
        'django-redis',  # Django Redis cache
    ]
    
    print("📦 Installing production dependencies...")
    
    for package in production_packages:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"⚠️  Failed to install {package} (optional)")
    
    return True

def run_security_checks():
    """Run Django security checks"""
    print("🔍 Running Django security checks...")
    
    try:
        result = subprocess.run([sys.executable, 'manage.py', 'check', '--deploy'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All security checks passed!")
        else:
            print("⚠️  Security check warnings:")
            print(result.stdout)
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running security checks: {e}")
    
    return True

def collect_static_files():
    """Collect static files for production"""
    print("📂 Collecting static files...")
    
    try:
        subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], 
                      check=True)
        print("✅ Static files collected successfully")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error collecting static files: {e}")
    
    return True

def create_superuser():
    """Prompt to create superuser"""
    print("\n👤 Would you like to create a superuser account? (y/n): ", end="")
    choice = input().lower().strip()
    
    if choice in ['y', 'yes']:
        try:
            subprocess.run([sys.executable, 'manage.py', 'createsuperuser'])
            print("✅ Superuser created successfully")
        except KeyboardInterrupt:
            print("\n⚠️  Superuser creation cancelled")
    
    return True

def generate_startup_scripts():
    """Generate production startup scripts"""
    
    # Gunicorn startup script
    gunicorn_script = """#!/bin/bash
# ZtionSec Production Startup Script

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Start Gunicorn server
exec gunicorn --bind 0.0.0.0:8000 \\
    --workers 3 \\
    --worker-class sync \\
    --worker-connections 1000 \\
    --max-requests 1000 \\
    --max-requests-jitter 100 \\
    --timeout 30 \\
    --keep-alive 2 \\
    --access-logfile logs/access.log \\
    --error-logfile logs/error.log \\
    --log-level info \\
    Ztionsec.wsgi:application
"""
    
    with open('start_production.sh', 'w') as f:
        f.write(gunicorn_script)
    
    os.chmod('start_production.sh', 0o755)
    print("✅ Created start_production.sh")
    
    # HTTPS startup script
    https_script = """#!/bin/bash
# ZtionSec HTTPS Production Startup Script

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Generate SSL certificates if they don't exist
if [ ! -f ssl/cert.pem ]; then
    echo "🔐 Generating SSL certificates..."
    python generate_ssl_cert.py
fi

# Start HTTPS server
exec gunicorn --bind 0.0.0.0:8443 \\
    --workers 3 \\
    --worker-class sync \\
    --certfile ssl/cert.pem \\
    --keyfile ssl/key.pem \\
    --access-logfile logs/https_access.log \\
    --error-logfile logs/https_error.log \\
    --log-level info \\
    Ztionsec.wsgi:application
"""
    
    with open('start_https_production.sh', 'w') as f:
        f.write(https_script)
    
    os.chmod('start_https_production.sh', 0o755)
    print("✅ Created start_https_production.sh")
    
    return True

def main():
    """Main deployment function"""
    print("🛡️  ZtionSec Production Deployment")
    print("=" * 50)
    
    steps = [
        ("Creating environment file", create_env_file),
        ("Setting up directories", setup_directories),
        ("Installing production dependencies", install_production_dependencies),
        ("Running security checks", run_security_checks),
        ("Collecting static files", collect_static_files),
        ("Creating startup scripts", generate_startup_scripts),
        ("Creating superuser", create_superuser),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        try:
            step_func()
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            return False
    
    print("\n🎉 Production deployment completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your actual API keys and domain")
    print("2. Configure your web server (nginx/apache) to proxy to Gunicorn")
    print("3. Set up SSL certificates for production domain")
    print("4. Start the production server: ./start_production.sh")
    print("5. For HTTPS: ./start_https_production.sh")
    print("\n🔒 Security Reminders:")
    print("- Change default passwords")
    print("- Configure firewall rules")
    print("- Set up regular backups")
    print("- Monitor security logs")
    
    return True

if __name__ == "__main__":
    main()
