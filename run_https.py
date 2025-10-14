#!/usr/bin/env python3
"""
HTTPS Development Server for ZtionSec
Runs Django development server with SSL/TLS support
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run Django development server with HTTPS"""
    
    # Check if certificates exist
    ssl_dir = Path(__file__).parent / 'ssl'
    cert_file = ssl_dir / 'cert.pem'
    key_file = ssl_dir / 'key.pem'
    
    if not cert_file.exists() or not key_file.exists():
        print("❌ SSL certificates not found!")
        print("🔧 Run: python generate_ssl_cert.py")
        return 1
    
    # Set environment variable for development HTTPS
    os.environ['DJANGO_DEVELOPMENT'] = '1'
    
    print("🚀 Starting ZtionSec HTTPS Development Server...")
    print("🔐 SSL Certificate: ✅")
    print("🌐 URL: https://127.0.0.1:8000/")
    print("⚠️  You'll see a security warning - click 'Advanced' and 'Proceed to 127.0.0.1'")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Try django-extensions runserver_plus first
        cmd = [
            sys.executable, 'manage.py', 'runserver_plus',
            '--cert-file', str(cert_file),
            '--key-file', str(key_file),
            '127.0.0.1:8000'
        ]
        
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError:
        print("💡 Installing django-extensions for HTTPS support...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'django-extensions'])
        
        # Try again
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to start HTTPS server")
            print("💡 Falling back to HTTP server...")
            subprocess.run([sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000'])
    
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        return 0

if __name__ == '__main__':
    sys.exit(main())
