#!/usr/bin/env python3
"""
SSL Certificate Generator for ZtionSec Local Development
Generates self-signed SSL certificates for HTTPS testing
"""

import os
import subprocess
import sys
from pathlib import Path

def generate_ssl_certificate():
    """Generate self-signed SSL certificate for local development"""
    
    # Create ssl directory
    ssl_dir = Path(__file__).parent / 'ssl'
    ssl_dir.mkdir(exist_ok=True)
    
    cert_file = ssl_dir / 'cert.pem'
    key_file = ssl_dir / 'key.pem'
    
    print("🔐 Generating SSL Certificate for ZtionSec...")
    print(f"📁 SSL Directory: {ssl_dir}")
    
    # OpenSSL command to generate self-signed certificate
    openssl_cmd = [
        'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
        '-keyout', str(key_file),
        '-out', str(cert_file),
        '-days', '365',
        '-nodes',
        '-subj', '/C=US/ST=Security/L=Analysis/O=ZtionSec/OU=Development/CN=localhost'
    ]
    
    try:
        # Check if OpenSSL is available
        subprocess.run(['openssl', 'version'], check=True, capture_output=True)
        
        # Generate certificate
        result = subprocess.run(openssl_cmd, check=True, capture_output=True, text=True)
        
        print("✅ SSL Certificate generated successfully!")
        print(f"📄 Certificate: {cert_file}")
        print(f"🔑 Private Key: {key_file}")
        
        # Set proper permissions
        os.chmod(key_file, 0o600)
        os.chmod(cert_file, 0o644)
        
        print("\n🚀 To run Django with HTTPS:")
        print(f"python manage.py runserver_plus --cert-file {cert_file} --key-file {key_file} 127.0.0.1:8000")
        print("\n📝 Or use the provided run_https.py script")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating certificate: {e}")
        print("💡 Make sure OpenSSL is installed on your system")
        return False
    except FileNotFoundError:
        print("❌ OpenSSL not found!")
        print("💡 Please install OpenSSL:")
        print("   - Ubuntu/Debian: sudo apt-get install openssl")
        print("   - macOS: brew install openssl")
        print("   - Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        return False

def create_https_runner():
    """Create a script to run Django with HTTPS"""
    
    runner_script = Path(__file__).parent / 'run_https.py'
    
    script_content = '''#!/usr/bin/env python3
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
        print("\\n🛑 Server stopped")
        return 0

if __name__ == '__main__':
    sys.exit(main())
'''
    
    with open(runner_script, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(runner_script, 0o755)
    
    print(f"📝 Created HTTPS runner script: {runner_script}")

def main():
    """Main function"""
    print("🛡️  ZtionSec SSL Certificate Generator")
    print("=" * 50)
    
    # Generate SSL certificate
    if generate_ssl_certificate():
        # Create HTTPS runner script
        create_https_runner()
        
        print("\n🎉 Setup Complete!")
        print("📋 Next steps:")
        print("1. Install django-extensions: pip install django-extensions")
        print("2. Run HTTPS server: python run_https.py")
        print("3. Visit: https://127.0.0.1:8000/")
        print("4. Accept the security warning (self-signed certificate)")
        
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
