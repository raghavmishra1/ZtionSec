#!/usr/bin/env python3
"""
Start ZtionSec HTTPS Development Server
Simple script to start the Django development server with SSL/TLS support
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the HTTPS development server"""
    
    print("🚀 Starting ZtionSec HTTPS Development Server...")
    print("=" * 50)
    
    # Kill any existing server processes
    try:
        subprocess.run(['pkill', '-f', 'python manage.py runserver_plus'], 
                      capture_output=True, timeout=5)
    except:
        pass  # Ignore errors if no processes to kill
    
    # Check if certificates exist
    ssl_dir = Path(__file__).parent / 'ssl'
    cert_file = ssl_dir / 'cert.pem'
    key_file = ssl_dir / 'key.pem'
    
    if not cert_file.exists() or not key_file.exists():
        print("❌ SSL certificates not found!")
        print("🔧 Run: python generate_ssl_cert.py")
        return 1
    
    # Set environment variables for development HTTPS
    os.environ['DJANGO_DEVELOPMENT'] = '1'
    os.environ['DISABLE_CSP'] = 'true'  # Disable CSP for development to avoid blocking
    
    print("🔐 SSL Certificate: ✅")
    print("🌐 Starting server at: https://127.0.0.1:8000/")
    print("⚠️  You'll see a security warning - click 'Advanced' and 'Proceed to 127.0.0.1'")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run the HTTPS development server
        cmd = [
            sys.executable, 'manage.py', 'runserver_plus',
            '--cert-file', str(cert_file),
            '--key-file', str(key_file),
            '127.0.0.1:8000'
        ]
        
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure you have installed: pip install django-extensions Werkzeug pyOpenSSL")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
