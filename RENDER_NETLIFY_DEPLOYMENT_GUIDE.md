# 🚀 ZtionSec: Render + Netlify Deployment Guide

## 🎯 **Architecture Overview**

This guide covers deploying ZtionSec with a **separated architecture**:
- **🔧 Backend API**: Django REST API on **Render.com** (Free)
- **🎨 Frontend**: Static HTML/CSS/JS on **Netlify** (Free)

### **Benefits of This Architecture:**
- ✅ **Better Performance**: Static frontend loads faster
- ✅ **Scalability**: Frontend and backend can scale independently  
- ✅ **Cost Effective**: Both platforms offer generous free tiers
- ✅ **Modern Stack**: API-first approach with clean separation
- ✅ **Easy Maintenance**: Update frontend without touching backend

---

## 📁 **Project Structure**

```
ZtionSec/
├── 🔧 Backend (Django API)
│   ├── scanner/
│   │   ├── api_views.py      # REST API endpoints
│   │   ├── serializers.py    # Data serialization
│   │   └── api_urls.py       # API URL routing
│   ├── Ztionsec/
│   │   └── settings_deploy.py # Production settings with CORS
│   ├── requirements.txt      # Python dependencies
│   └── render.yaml          # Render deployment config
│
└── 🎨 Frontend (Static)
    ├── frontend/
    │   ├── index.html       # Main application
    │   ├── css/style.css    # Styling
    │   └── js/app.js        # JavaScript logic
    └── netlify.toml         # Netlify deployment config
```

---

## 🔧 **Part 1: Deploy Backend API to Render**

### **Step 1: Prepare Backend Repository**

```bash
# Create a separate repository for backend (optional but recommended)
git init ztionsec-backend
cd ztionsec-backend

# Copy backend files
cp -r /path/to/ZtionSec/* .

# Remove frontend directory (not needed for backend)
rm -rf frontend/

# Commit backend code
git add .
git commit -m "ZtionSec Backend API"
git remote add origin https://github.com/yourusername/ztionsec-backend.git
git push -u origin main
```

### **Step 2: Deploy to Render**

1. **Go to [render.com](https://render.com)** and sign up
2. **Connect GitHub** repository
3. **Create Web Service**:
   - **Repository**: `ztionsec-backend`
   - **Name**: `ztionsec-api`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**: 
     ```bash
     gunicorn Ztionsec.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
     ```

4. **Add Environment Variables**:
   ```
   DJANGO_SETTINGS_MODULE=Ztionsec.settings_deploy
   DEBUG=False
   SECRET_KEY=auto-generated-by-render
   CORS_ALLOW_ALL_ORIGINS=True
   ENABLE_PORT_SCANNING=False
   RATE_LIMIT_SCANS_PER_HOUR=5
   ```

5. **Create PostgreSQL Database**:
   - Click **"New +"** → **"PostgreSQL"**
   - Name: `ztionsec-db`
   - Connect to web service (DATABASE_URL will be auto-configured)

6. **Deploy**: Click **"Create Web Service"**

### **Step 3: Test Backend API**

Once deployed, test your API endpoints:

```bash
# Replace with your actual Render URL
API_URL="https://ztionsec-api.onrender.com"

# Test health check
curl $API_URL/api/v1/health/

# Test stats endpoint
curl $API_URL/api/v1/stats/

# Test basic scan
curl -X POST $API_URL/api/v1/scan/basic/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

## 🎨 **Part 2: Deploy Frontend to Netlify**

### **Step 1: Prepare Frontend Repository**

```bash
# Create separate repository for frontend
git init ztionsec-frontend
cd ztionsec-frontend

# Copy only frontend files
mkdir frontend
cp -r /path/to/ZtionSec/frontend/* frontend/
cp /path/to/ZtionSec/netlify.toml .

# Update API URL in frontend
# Edit frontend/js/app.js and replace:
const API_BASE_URL = 'https://your-ztionsec-api.onrender.com/api/v1';
# With your actual Render URL

# Commit frontend code
git add .
git commit -m "ZtionSec Frontend"
git remote add origin https://github.com/yourusername/ztionsec-frontend.git
git push -u origin main
```

### **Step 2: Deploy to Netlify**

1. **Go to [netlify.com](https://netlify.com)** and sign up
2. **Connect GitHub** repository
3. **Create New Site**:
   - **Repository**: `ztionsec-frontend`
   - **Build Command**: `echo 'Static site - no build needed'`
   - **Publish Directory**: `frontend`
   - **Deploy Site**

4. **Configure Custom Domain** (Optional):
   - Go to **Site Settings** → **Domain Management**
   - Add custom domain: `ztionsec.yourdomain.com`

### **Step 3: Update CORS Settings**

Update your backend's CORS settings to allow your Netlify domain:

```python
# In Ztionsec/settings_deploy.py
CORS_ALLOWED_ORIGINS = [
    "https://your-site.netlify.app",
    "https://ztionsec.yourdomain.com",  # If using custom domain
    "http://localhost:3000",  # For local development
]
```

Redeploy your Render backend after this change.

---

## 🔗 **Part 3: Connect Frontend to Backend**

### **Update API Configuration**

Edit `frontend/js/app.js`:

```javascript
// Replace this line:
const API_BASE_URL = 'https://your-ztionsec-api.onrender.com/api/v1';

// With your actual Render API URL:
const API_BASE_URL = 'https://ztionsec-api.onrender.com/api/v1';
```

### **Update Netlify Configuration**

Edit `netlify.toml`:

```toml
# Update the API proxy redirect
[[redirects]]
  from = "/api/*"
  to = "https://ztionsec-api.onrender.com/api/:splat"  # Your actual API URL
  status = 200
  force = true

# Update CSP header
[[headers]]
  for = "/*"
  [headers.values]
    Content-Security-Policy = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' data: https://cdnjs.cloudflare.com; connect-src 'self' https://ztionsec-api.onrender.com;"
```

---

## 🔧 **Part 4: File Control & Management**

### **Backend File Management**

For file uploads and management on Render:

```python
# In settings_deploy.py
import os

# Media files configuration for Render
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# For production file storage (optional - use cloud storage)
if 'CLOUDINARY_URL' in os.environ:
    # Cloudinary configuration for file storage
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### **File Upload API Endpoint**

Add to `scanner/api_views.py`:

```python
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage

@api_view(['POST'])
@permission_classes([AllowAny])
def api_file_upload(request):
    """Handle file uploads"""
    try:
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=400)
        
        file = request.FILES['file']
        
        # Save file
        filename = default_storage.save(f'uploads/{file.name}', file)
        file_url = default_storage.url(filename)
        
        return Response({
            'success': True,
            'filename': filename,
            'url': file_url,
            'size': file.size
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)
```

### **Frontend File Upload**

Add to `frontend/js/app.js`:

```javascript
// File upload function
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE_URL}/upload/`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            return result;
        } else {
            throw new Error('Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
}
```

---

## 📊 **Part 5: Monitoring & Analytics**

### **Backend Monitoring (Render)**

```python
# Add to api_views.py
@api_view(['GET'])
@permission_classes([AllowAny])
def api_system_status(request):
    """System status and health metrics"""
    import psutil
    from django.db import connection
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        return Response({
            'status': 'healthy',
            'database': 'connected',
            'cpu_usage': f"{cpu_percent}%",
            'memory_usage': f"{memory.percent}%",
            'uptime': 'Available',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)
```

### **Frontend Analytics**

Add Google Analytics or similar to `frontend/index.html`:

```html
<!-- Google Analytics (optional) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

---

## 🚀 **Part 6: Deployment Automation**

### **GitHub Actions for Auto-Deploy**

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy ZtionSec

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    if: contains(github.event.head_commit.modified, 'backend/')
    steps:
      - uses: actions/checkout@v3
      - name: Trigger Render Deploy
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK }}"
  
  deploy-frontend:
    runs-on: ubuntu-latest
    if: contains(github.event.head_commit.modified, 'frontend/')
    steps:
      - uses: actions/checkout@v3
      - name: Trigger Netlify Deploy
        run: |
          curl -X POST "${{ secrets.NETLIFY_BUILD_HOOK }}"
```

---

## 🔒 **Part 7: Security Configuration**

### **Backend Security Headers**

```python
# In settings_deploy.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# API Rate Limiting
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle'
]
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/hour',
    'user': '1000/hour'
}
```

### **Frontend Security**

Update `netlify.toml` with security headers:

```toml
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Strict-Transport-Security = "max-age=31536000; includeSubDomains; preload"
```

---

## 📋 **Deployment Checklist**

### **Backend (Render) ✅**
- [ ] ✅ **Repository connected**
- [ ] ✅ **Environment variables set**
- [ ] ✅ **PostgreSQL database connected**
- [ ] ✅ **API endpoints working**
- [ ] ✅ **CORS configured**
- [ ] ✅ **Health check passing**

### **Frontend (Netlify) ✅**
- [ ] ✅ **Repository connected**
- [ ] ✅ **Build settings configured**
- [ ] ✅ **API URL updated**
- [ ] ✅ **Custom domain configured** (optional)
- [ ] ✅ **Security headers set**
- [ ] ✅ **Site accessible**

### **Integration ✅**
- [ ] ✅ **Frontend connects to backend**
- [ ] ✅ **Scans working end-to-end**
- [ ] ✅ **CORS allowing frontend domain**
- [ ] ✅ **File uploads working** (if implemented)
- [ ] ✅ **Monitoring configured**

---

## 🎯 **Final URLs**

After deployment, you'll have:

- **🔧 Backend API**: `https://ztionsec-api.onrender.com`
  - Health: `/api/v1/health/`
  - Stats: `/api/v1/stats/`
  - Scans: `/api/v1/scan/basic/`

- **🎨 Frontend**: `https://your-site.netlify.app`
  - Main app with full UI
  - Connects to backend API
  - Fast static hosting

---

## 🆘 **Troubleshooting**

### **Common Issues**

#### **CORS Errors**
```bash
# Check backend CORS settings
# Ensure frontend domain is in CORS_ALLOWED_ORIGINS
```

#### **API Connection Failed**
```bash
# Check if backend is sleeping (Render free tier)
curl https://ztionsec-api.onrender.com/api/v1/health/
```

#### **Build Failures**
```bash
# Check Render build logs
# Ensure all dependencies in requirements.txt
```

### **Debug Commands**

```bash
# Test backend locally
python manage.py runserver --settings=Ztionsec.settings_deploy

# Test frontend locally
cd frontend && python -m http.server 8080

# Check API connectivity
curl -X POST https://your-api.onrender.com/api/v1/scan/basic/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

## 🎉 **Success!**

You now have a **production-ready ZtionSec platform** with:

- ✅ **Scalable Architecture**: Backend API + Static Frontend
- ✅ **Free Hosting**: Render + Netlify free tiers
- ✅ **Modern Stack**: REST API with responsive frontend
- ✅ **High Performance**: Fast static frontend, optimized backend
- ✅ **Easy Maintenance**: Independent deployments
- ✅ **Professional Setup**: Custom domains, security headers, monitoring

**Your ZtionSec platform is now live and ready to scan the web! 🌍🔒**
