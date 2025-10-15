# ZtionSec Production Deployment Guide
## Senior Developer Implementation - Enterprise Grade

### 🚀 Quick Start Production Deployment

#### Prerequisites
- Ubuntu 20.04+ or CentOS 8+
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Nginx 1.18+
- 4GB RAM minimum (8GB recommended)
- 20GB disk space minimum

#### 1. Automated Deployment (Recommended)
```bash
# Clone repository
git clone https://github.com/your-org/ztionsec.git
cd ztionsec

# Run automated deployment
sudo python3 production_deploy.py

# Follow the prompts and configure environment variables
```

#### 2. Manual Deployment Steps

##### System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx certbot python3-certbot-nginx

# Create system user
sudo useradd -m -s /bin/bash ztionsec
sudo usermod -aG www-data ztionsec
```

##### Database Configuration
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE ztionsec_prod;
CREATE USER ztionsec WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ztionsec_prod TO ztionsec;
ALTER USER ztionsec CREATEDB;
\q
```

##### Application Setup
```bash
# Switch to ztionsec user
sudo -u ztionsec -i

# Clone and setup application
git clone https://github.com/your-org/ztionsec.git
cd ztionsec

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary redis django-redis

# Configure environment
cp .env.production .env
# Edit .env with your production values

# Run Django setup
export DJANGO_SETTINGS_MODULE=Ztionsec.settings_production
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

##### SSL Certificate Setup
```bash
# Using Let's Encrypt (Recommended)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Or create self-signed for testing
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/ztionsec.key \
    -out /etc/ssl/certs/ztionsec.crt
```

##### Nginx Configuration
```bash
# Copy nginx configuration
sudo cp /home/ztionsec/ztionsec/nginx.conf /etc/nginx/sites-available/ztionsec
sudo ln -s /etc/nginx/sites-available/ztionsec /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

##### Systemd Service Setup
```bash
# Copy service files
sudo cp /home/ztionsec/ztionsec/systemd/ztionsec.service /etc/systemd/system/
sudo cp /home/ztionsec/ztionsec/systemd/ztionsec.socket /etc/systemd/system/

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable ztionsec.socket
sudo systemctl start ztionsec.socket
sudo systemctl enable ztionsec.service
sudo systemctl start ztionsec.service
```

### 🔧 Configuration

#### Environment Variables (.env.production)
```bash
# Core Django Settings
SECRET_KEY=your-super-secret-production-key-change-this
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=ztionsec_prod
DB_USER=ztionsec
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis Cache
REDIS_URL=redis://127.0.0.1:6379/1

# API Keys
HAVEIBEENPWNED_API_KEY=your_hibp_api_key
SHODAN_API_KEY=your_shodan_api_key
CENSYS_API_ID=your_censys_api_id
CENSYS_API_SECRET=your_censys_api_secret

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Security
ADMIN_URL=secure-admin-path/
```

#### Security Checklist
- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY (50+ characters)
- [ ] HTTPS enabled with valid SSL certificate
- [ ] Database password is strong and unique
- [ ] Admin URL is changed from default
- [ ] Firewall configured (ports 80, 443 only)
- [ ] Regular security updates scheduled
- [ ] Backup strategy implemented
- [ ] Monitoring and logging configured

### 🔍 Monitoring & Maintenance

#### Health Checks
```bash
# Check application status
sudo systemctl status ztionsec
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis

# Check logs
sudo journalctl -u ztionsec -f
tail -f /var/log/ztionsec/django.log
tail -f /var/log/nginx/access.log
```

#### Performance Monitoring
```bash
# Database performance
sudo -u postgres psql ztionsec_prod -c "SELECT * FROM pg_stat_activity;"

# Redis performance
redis-cli info stats

# System resources
htop
df -h
free -h
```

#### Backup Strategy
```bash
# Database backup
sudo -u postgres pg_dump ztionsec_prod > backup_$(date +%Y%m%d).sql

# Application backup
tar -czf ztionsec_backup_$(date +%Y%m%d).tar.gz /home/ztionsec/ztionsec

# Automated backup script (add to crontab)
0 2 * * * /home/ztionsec/scripts/backup.sh
```

### 🚨 Troubleshooting

#### Common Issues

**Application won't start:**
```bash
# Check logs
sudo journalctl -u ztionsec -n 50

# Check configuration
python manage.py check --deploy

# Test database connection
python manage.py dbshell
```

**SSL Certificate Issues:**
```bash
# Renew Let's Encrypt certificate
sudo certbot renew --dry-run

# Check certificate expiry
openssl x509 -in /etc/ssl/certs/ztionsec.crt -text -noout
```

**Performance Issues:**
```bash
# Check database queries
python manage.py shell
>>> from django.db import connection
>>> print(connection.queries)

# Monitor Redis
redis-cli monitor

# Check system resources
iostat -x 1
```

### 📊 Scaling Considerations

#### Horizontal Scaling
- Load balancer (HAProxy/Nginx)
- Multiple application servers
- Database replication
- Redis clustering
- CDN for static files

#### Vertical Scaling
- Increase server resources
- Optimize database queries
- Enable caching layers
- Compress static files

### 🔐 Security Hardening

#### Additional Security Measures
```bash
# Fail2ban for brute force protection
sudo apt install fail2ban
sudo systemctl enable fail2ban

# UFW firewall
sudo ufw enable
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443

# Automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

#### Security Monitoring
- Set up log monitoring (ELK stack)
- Configure intrusion detection (OSSEC)
- Regular security scans
- Vulnerability assessments

### 📈 Performance Optimization

#### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX CONCURRENTLY idx_security_scan_url ON scanner_securityscan(url);
CREATE INDEX CONCURRENTLY idx_security_scan_date ON scanner_securityscan(scan_date);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM scanner_securityscan WHERE url = 'https://example.com';
```

#### Caching Strategy
```python
# Redis caching configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 🔄 Updates & Maintenance

#### Application Updates
```bash
# Backup before update
./backup.sh

# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart ztionsec
```

#### Database Maintenance
```bash
# Vacuum and analyze
sudo -u postgres psql ztionsec_prod -c "VACUUM ANALYZE;"

# Check database size
sudo -u postgres psql ztionsec_prod -c "SELECT pg_size_pretty(pg_database_size('ztionsec_prod'));"
```

### 📞 Support & Resources

#### Documentation
- [API Documentation](https://yourdomain.com/api/docs/)
- [User Manual](https://yourdomain.com/docs/)
- [Security Guide](https://yourdomain.com/security/)

#### Support Channels
- Email: ztionsec@zohomail.in
- Documentation: https://docs.yourdomain.com
- GitHub Issues: https://github.com/your-org/ztionsec/issues

#### Emergency Contacts
- System Administrator: ztionsec@zohomail.in
- Security Team: ztionsec@zohomail.in
- On-call Support: +1-XXX-XXX-XXXX
