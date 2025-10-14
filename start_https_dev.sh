#!/bin/bash
# ZtionSec HTTPS Development Server
# Starts the Django development server with SSL/TLS encryption

echo "🛡️  Starting ZtionSec HTTPS Development Server"
echo "================================================"

# Check if SSL certificates exist
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    echo "🔐 SSL certificates not found. Generating..."
    python generate_ssl_cert.py
fi

echo "🚀 Starting HTTPS server at https://127.0.0.1:8000"
echo "📋 Features enabled:"
echo "   ✅ SSL/TLS encryption"
echo "   ✅ Security headers (HSTS, CSP, X-Frame-Options, etc.)"
echo "   ✅ Rate limiting and security monitoring"
echo "   ✅ CSRF protection"
echo "   ✅ Admin panel protection"
echo ""
echo "🌐 Access your application:"
echo "   - Main site: https://127.0.0.1:8000"
echo "   - Admin panel: https://127.0.0.1:8000/secure-admin-panel-ztionsec-2024/"
echo ""
echo "⚠️  Note: You'll see a security warning for self-signed certificate"
echo "   Click 'Advanced' → 'Proceed to 127.0.0.1 (unsafe)' to continue"
echo ""
echo "🔧 To stop the server: Press Ctrl+C"
echo "================================================"

# Start the HTTPS development server
python manage.py runserver_plus --cert-file ssl/cert.pem --key-file ssl/key.pem 127.0.0.1:8000
