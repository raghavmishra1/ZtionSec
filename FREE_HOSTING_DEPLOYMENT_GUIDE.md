# 🚀 ZtionSec Free Hosting Deployment Guide

## 📋 **Overview**

This guide covers deploying ZtionSec on free hosting platforms with proper monitoring setup. Since ZtionSec is a Django application, **Netlify is NOT suitable** (it's for static sites only). We'll focus on the best free options for Django apps.

---

## 🎯 **Recommended Free Hosting Platforms**

### **1. 🥇 Render.com (RECOMMENDED)**
- ✅ **Free PostgreSQL database** (90 days, then sleeps)
- ✅ **Automatic deployments** from GitHub
- ✅ **Custom domains** supported
- ✅ **SSL certificates** included
- ⚠️ **Sleeps after 15 minutes** of inactivity

### **2. 🥈 Railway.app**
- ✅ **$5 free credit monthly**
- ✅ **PostgreSQL included**
- ✅ **Fast deployments**
- ✅ **Great developer experience**

### **3. 🥉 PythonAnywhere**
- ✅ **Always-on free tier**
- ✅ **No sleeping**
- ⚠️ **Limited to 1 web app**
- ⚠️ **Custom domains require paid plan**

---

## 🔧 **Pre-Deployment Setup**

### **1. Environment Variables**
Create a `.env` file for production:

```bash
# Core Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here-change-this
DJANGO_SETTINGS_MODULE=Ztionsec.settings_deploy
ALLOWED_HOSTS=your-domain.com,your-app.onrender.com

# Database (will be auto-configured by hosting platform)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Security Settings
SECURE_SSL_REDIRECT=True

# API Keys (Optional - for enhanced features)
HAVEIBEENPWNED_API_KEY=your-hibp-key
SHODAN_API_KEY=your-shodan-key
CENSYS_API_ID=your-censys-id
CENSYS_API_SECRET=your-censys-secret

# Rate Limiting (Adjusted for free hosting)
RATE_LIMIT_SCANS_PER_HOUR=5
RATE_LIMIT_API_CALLS_PER_HOUR=50
ENABLE_PORT_SCANNING=False
```

### **2. GitHub Repository Setup**
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial ZtionSec deployment"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/ztionsec.git
git branch -M main
git push -u origin main
```

---

## 🚀 **Deployment Instructions**

## **Option 1: Render.com Deployment**

### **Step 1: Create Render Account**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Connect your GitHub repository

### **Step 2: Create Web Service**
1. Click **"New +"** → **"Web Service"**
2. Connect your ZtionSec repository
3. Configure settings:
   - **Name**: `ztionsec`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**: 
     ```bash
     gunicorn Ztionsec.wsgi:application
     ```

### **Step 3: Add Environment Variables**
In Render dashboard, add these environment variables:
```
DJANGO_SETTINGS_MODULE=Ztionsec.settings_deploy
DEBUG=False
SECRET_KEY=your-secret-key-here
PYTHON_VERSION=3.11.9
```

### **Step 4: Create Database**
1. Click **"New +"** → **"PostgreSQL"**
2. Name: `ztionsec-db`
3. Copy the **Internal Database URL**
4. Add to web service environment variables:
   ```
   DATABASE_URL=postgresql://...
   ```

### **Step 5: Deploy**
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Your app will be available at: `https://ztionsec.onrender.com`

---

## **Option 2: Railway.app Deployment**

### **Step 1: Create Railway Account**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Install Railway CLI (optional):
   ```bash
   npm install -g @railway/cli
   railway login
   ```

### **Step 2: Deploy from GitHub**
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your ZtionSec repository
4. Railway will auto-detect Django and deploy

### **Step 3: Add Database**
1. Click **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway will automatically set `DATABASE_URL`

### **Step 4: Configure Environment Variables**
```
DJANGO_SETTINGS_MODULE=Ztionsec.settings_deploy
DEBUG=False
SECRET_KEY=your-secret-key-here
RAILWAY_STATIC_URL=/static/
```

---

## **Option 3: PythonAnywhere Deployment**

### **Step 1: Create Account**
1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Create free account
3. Open **Bash console**

### **Step 2: Clone Repository**
```bash
git clone https://github.com/yourusername/ztionsec.git
cd ztionsec
```

### **Step 3: Setup Virtual Environment**
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Step 4: Configure Web App**
1. Go to **Web** tab
2. Click **"Add a new web app"**
3. Choose **Manual configuration** → **Python 3.10**
4. Set **Source code**: `/home/yourusername/ztionsec`
5. Set **Virtualenv**: `/home/yourusername/ztionsec/venv`

### **Step 5: Configure WSGI**
Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:
```python
import os
import sys

path = '/home/yourusername/ztionsec'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'Ztionsec.settings_deploy'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

---

## 📊 **Website Monitoring Setup**

### **1. Free Monitoring Services**

#### **UptimeRobot (Recommended)**
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Create free account (50 monitors)
3. Add monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://your-app.onrender.com`
   - **Interval**: 5 minutes
   - **Alert contacts**: Your email

#### **Pingdom**
1. Go to [pingdom.com](https://pingdom.com)
2. Free plan: 1 monitor
3. Setup similar to UptimeRobot

#### **StatusCake**
1. Go to [statuscake.com](https://statuscake.com)
2. Free plan: 10 monitors
3. More detailed monitoring options

### **2. Custom Monitoring Script**

Use the included monitoring script:

```bash
# Install dependencies
pip install requests

# Configure monitoring
cd monitoring/
nano monitoring_config.json  # Update with your URLs

# Run monitoring
python uptime_monitor.py --once  # Single check
python uptime_monitor.py         # Continuous monitoring
```

### **3. GitHub Actions Monitoring**

Create `.github/workflows/monitor.yml`:
```yaml
name: Website Monitoring
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install requests
      - name: Run monitoring
        run: python monitoring/uptime_monitor.py --once
```

---

## 🔒 **Security Considerations for Free Hosting**

### **1. Environment Variables**
- ✅ **Never commit** `.env` files
- ✅ **Use platform environment variables**
- ✅ **Rotate secrets regularly**

### **2. Rate Limiting**
```python
# Adjusted for free hosting
RATE_LIMIT_SCANS_PER_HOUR = 5
RATE_LIMIT_API_CALLS_PER_HOUR = 50
ENABLE_PORT_SCANNING = False  # Disabled to avoid abuse
```

### **3. Database Security**
- ✅ **Use PostgreSQL** (not SQLite in production)
- ✅ **Enable SSL** connections
- ✅ **Regular backups**

---

## 🎛️ **Performance Optimization for Free Hosting**

### **1. Static Files**
```python
# settings_deploy.py
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### **2. Database Optimization**
```python
# Reduce database queries
DATABASES['default']['CONN_MAX_AGE'] = 60
```

### **3. Caching**
```python
# Use database caching for free hosting
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. App Sleeping (Render/Railway)**
**Problem**: App sleeps after 15 minutes of inactivity
**Solution**: 
- Use UptimeRobot to ping every 5 minutes
- Implement keep-alive endpoint

#### **2. Database Connection Errors**
**Problem**: Database connection issues
**Solution**:
```python
# Check DATABASE_URL format
DATABASE_URL=postgresql://user:password@host:port/dbname
```

#### **3. Static Files Not Loading**
**Problem**: CSS/JS files not found
**Solution**:
```bash
python manage.py collectstatic --noinput
```

#### **4. Memory Limits**
**Problem**: App crashes due to memory usage
**Solution**:
- Disable resource-intensive features
- Optimize database queries
- Use pagination

### **Debug Commands**
```bash
# Check logs (Render)
render logs --service your-service-name

# Check logs (Railway)
railway logs

# Local testing
python manage.py check --deploy
python manage.py runserver --settings=Ztionsec.settings_deploy
```

---

## 📈 **Monitoring Dashboard Setup**

### **1. Simple HTML Status Page**
Create a status page at `/status/`:

```python
# views.py
def status_page(request):
    return render(request, 'status.html', {
        'uptime': get_uptime(),
        'last_scan': get_last_scan_time(),
        'total_scans': get_total_scans()
    })
```

### **2. Health Check Endpoint**
```python
# urls.py
path('health/', health_check, name='health_check'),

# views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)
```

---

## 🎉 **Post-Deployment Checklist**

- [ ] ✅ **App deployed successfully**
- [ ] ✅ **Database connected**
- [ ] ✅ **Static files loading**
- [ ] ✅ **Admin panel accessible**
- [ ] ✅ **Security scan working**
- [ ] ✅ **Monitoring setup**
- [ ] ✅ **Custom domain configured** (optional)
- [ ] ✅ **SSL certificate active**
- [ ] ✅ **Environment variables secure**
- [ ] ✅ **Backup strategy in place**

---

## 🆘 **Support & Resources**

### **Documentation**
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Render Django Guide](https://render.com/docs/deploy-django)
- [Railway Django Guide](https://docs.railway.app/guides/django)

### **Community**
- [ZtionSec GitHub Issues](https://github.com/yourusername/ztionsec/issues)
- [Django Discord](https://discord.gg/xcRH6mN4fa)
- [Render Community](https://community.render.com/)

---

## 🎯 **Next Steps**

1. **Deploy to your chosen platform**
2. **Setup monitoring**
3. **Configure custom domain**
4. **Add API keys for enhanced features**
5. **Setup automated backups**
6. **Monitor performance and optimize**

**Your ZtionSec platform will be live and accessible worldwide! 🌍**
