#!/usr/bin/env python3
"""
Production Deployment Script for ZtionSec
Senior Developer Implementation - Enterprise Grade
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class ProductionDeployer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.venv_path = self.base_dir / 'venv'
        
    def run_command(self, command, check=True):
        """Run shell command with error handling"""
        print(f"Running: {command}")
        try:
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            raise
    
    def check_prerequisites(self):
        """Check system prerequisites"""
        print("🔍 Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8+ required")
        
        # Check required system packages
        required_packages = ['nginx', 'postgresql', 'redis-server']
        for package in required_packages:
            result = subprocess.run(f"which {package}", shell=True, 
                                  capture_output=True)
            if result.returncode != 0:
                print(f"⚠️  {package} not found. Install with: sudo apt install {package}")
        
        print("✅ Prerequisites checked")
    
    def setup_environment(self):
        """Setup production environment"""
        print("🔧 Setting up production environment...")
        
        # Create virtual environment if it doesn't exist
        if not self.venv_path.exists():
            self.run_command(f"python3 -m venv {self.venv_path}")
        
        # Activate virtual environment and install requirements
        pip_path = self.venv_path / 'bin' / 'pip'
        self.run_command(f"{pip_path} install --upgrade pip")
        self.run_command(f"{pip_path} install -r requirements.txt")
        self.run_command(f"{pip_path} install gunicorn psycopg2-binary redis django-redis")
        
        print("✅ Environment setup complete")
    
    def setup_database(self):
        """Setup production database"""
        print("🗄️  Setting up database...")
        
        # Create database user and database
        db_commands = [
            "sudo -u postgres createuser --createdb ztionsec",
            "sudo -u postgres createdb ztionsec_prod -O ztionsec",
            "sudo -u postgres psql -c \"ALTER USER ztionsec WITH PASSWORD 'secure_password_123';\""
        ]
        
        for cmd in db_commands:
            try:
                self.run_command(cmd, check=False)
            except subprocess.CalledProcessError:
                print(f"Database command failed (may already exist): {cmd}")
        
        print("✅ Database setup complete")
    
    def configure_nginx(self):
        """Configure Nginx"""
        print("🌐 Configuring Nginx...")
        
        nginx_config = """
server {
    listen 80;
    server_name ztionsec.com www.ztionsec.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ztionsec.com www.ztionsec.com;
    
    ssl_certificate /etc/ssl/certs/ztionsec.crt;
    ssl_certificate_key /etc/ssl/private/ztionsec.key;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    client_max_body_size 10M;
    
    location /static/ {
        alias /home/ztionsec/ZtionSec/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /home/ztionsec/ZtionSec/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
"""
        
        # Write Nginx configuration
        nginx_config_path = "/etc/nginx/sites-available/ztionsec"
        with open(nginx_config_path, 'w') as f:
            f.write(nginx_config)
        
        # Enable site
        self.run_command(f"sudo ln -sf {nginx_config_path} /etc/nginx/sites-enabled/")
        self.run_command("sudo nginx -t")
        self.run_command("sudo systemctl reload nginx")
        
        print("✅ Nginx configured")
    
    def setup_systemd_service(self):
        """Setup systemd service for Gunicorn"""
        print("⚙️  Setting up systemd service...")
        
        service_config = f"""
[Unit]
Description=ZtionSec Gunicorn daemon
Requires=ztionsec.socket
After=network.target

[Service]
Type=notify
User=ztionsec
Group=www-data
RuntimeDirectory=gunicorn
WorkingDirectory={self.base_dir}
ExecStart={self.venv_path}/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn/ztionsec.sock Ztionsec.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
"""
        
        socket_config = """
[Unit]
Description=ZtionSec gunicorn socket

[Socket]
ListenStream=/run/gunicorn/ztionsec.sock
SocketUser=www-data

[Install]
WantedBy=sockets.target
"""
        
        # Write service files
        with open("/etc/systemd/system/ztionsec.service", 'w') as f:
            f.write(service_config)
        
        with open("/etc/systemd/system/ztionsec.socket", 'w') as f:
            f.write(socket_config)
        
        # Enable and start services
        self.run_command("sudo systemctl daemon-reload")
        self.run_command("sudo systemctl enable ztionsec.socket")
        self.run_command("sudo systemctl start ztionsec.socket")
        
        print("✅ Systemd service configured")
    
    def run_django_setup(self):
        """Run Django setup commands"""
        print("🐍 Running Django setup...")
        
        python_path = self.venv_path / 'bin' / 'python'
        
        # Set production environment
        os.environ['DJANGO_SETTINGS_MODULE'] = 'Ztionsec.settings_production'
        
        commands = [
            f"{python_path} manage.py collectstatic --noinput",
            f"{python_path} manage.py migrate",
            f"{python_path} manage.py check --deploy",
        ]
        
        for cmd in commands:
            self.run_command(cmd)
        
        print("✅ Django setup complete")
    
    def setup_ssl_certificates(self):
        """Setup SSL certificates"""
        print("🔒 Setting up SSL certificates...")
        
        # Create self-signed certificate for testing
        # In production, use Let's Encrypt or proper CA certificates
        ssl_commands = [
            "sudo mkdir -p /etc/ssl/private",
            "sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 "
            "-keyout /etc/ssl/private/ztionsec.key "
            "-out /etc/ssl/certs/ztionsec.crt "
            "-subj '/C=US/ST=State/L=City/O=ZtionSec/CN=ztionsec.com'",
            "sudo chmod 600 /etc/ssl/private/ztionsec.key"
        ]
        
        for cmd in ssl_commands:
            self.run_command(cmd)
        
        print("✅ SSL certificates configured")
    
    def setup_monitoring(self):
        """Setup monitoring and logging"""
        print("📊 Setting up monitoring...")
        
        # Create log directories
        log_dirs = ["/var/log/ztionsec", "/var/log/nginx"]
        for log_dir in log_dirs:
            self.run_command(f"sudo mkdir -p {log_dir}")
            self.run_command(f"sudo chown ztionsec:ztionsec {log_dir}")
        
        # Setup log rotation
        logrotate_config = """
/var/log/ztionsec/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ztionsec ztionsec
    postrotate
        systemctl reload ztionsec
    endscript
}
"""
        
        with open("/etc/logrotate.d/ztionsec", 'w') as f:
            f.write(logrotate_config)
        
        print("✅ Monitoring configured")
    
    def deploy(self):
        """Run full deployment"""
        print("🚀 Starting ZtionSec Production Deployment...")
        
        try:
            self.check_prerequisites()
            self.setup_environment()
            self.setup_database()
            self.setup_ssl_certificates()
            self.run_django_setup()
            self.configure_nginx()
            self.setup_systemd_service()
            self.setup_monitoring()
            
            print("\n🎉 Deployment completed successfully!")
            print("\n📋 Next steps:")
            print("1. Update /etc/hosts or DNS to point to your server")
            print("2. Configure firewall (ufw allow 80,443)")
            print("3. Set up proper SSL certificates (Let's Encrypt)")
            print("4. Configure environment variables in .env.production")
            print("5. Create superuser: python manage.py createsuperuser")
            print("\n🌐 Your ZtionSec platform should be available at https://ztionsec.com")
            
        except Exception as e:
            print(f"\n❌ Deployment failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    deployer = ProductionDeployer()
    deployer.deploy()
