#!/usr/bin/env python3
"""
ZtionSec Separated Architecture Deployment Script
Prepares backend for Render and frontend for Netlify
"""

import os
import sys
import shutil
import json
import subprocess
from pathlib import Path

class SeparatedDeployment:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend-deploy"
        self.frontend_dir = self.project_root / "frontend-deploy"
        
    def create_backend_deployment(self):
        """Create backend deployment directory"""
        print("🔧 Preparing backend for Render deployment...")
        
        # Create backend directory
        if self.backend_dir.exists():
            shutil.rmtree(self.backend_dir)
        self.backend_dir.mkdir()
        
        # Copy backend files
        backend_files = [
            'manage.py',
            'requirements.txt',
            'render.yaml',
            'railway.toml',
            'Procfile',
            'runtime.txt',
            'Ztionsec/',
            'scanner/',
            'templates/',
            'static/',
            'monitoring/',
            '.gitignore'
        ]
        
        for file_path in backend_files:
            src = self.project_root / file_path
            dst = self.backend_dir / file_path
            
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                print(f"✅ Copied {file_path}")
        
        # Create backend-specific .env
        env_content = """# ZtionSec Backend API Environment Variables
DEBUG=False
DJANGO_SETTINGS_MODULE=Ztionsec.settings_deploy
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=*
CORS_ALLOW_ALL_ORIGINS=True
ENABLE_PORT_SCANNING=False
RATE_LIMIT_SCANS_PER_HOUR=5
RATE_LIMIT_API_CALLS_PER_HOUR=50

# Database (will be auto-configured by Render)
# DATABASE_URL=postgresql://user:password@host:port/dbname

# Optional API Keys
HAVEIBEENPWNED_API_KEY=
SHODAN_API_KEY=
CENSYS_API_ID=
CENSYS_API_SECRET=
"""
        
        with open(self.backend_dir / '.env.example', 'w') as f:
            f.write(env_content)
        
        print("✅ Backend deployment ready in backend-deploy/")
        return True
    
    def create_frontend_deployment(self):
        """Create frontend deployment directory"""
        print("🎨 Preparing frontend for Netlify deployment...")
        
        # Create frontend directory
        if self.frontend_dir.exists():
            shutil.rmtree(self.frontend_dir)
        self.frontend_dir.mkdir()
        
        # Copy frontend files
        frontend_source = self.project_root / "frontend"
        if frontend_source.exists():
            shutil.copytree(frontend_source, self.frontend_dir / "frontend")
        else:
            print("❌ Frontend directory not found!")
            return False
        
        # Copy configuration files
        config_files = ['netlify.toml', '.gitignore']
        for file_path in config_files:
            src = self.project_root / file_path
            dst = self.frontend_dir / file_path
            if src.exists():
                shutil.copy2(src, dst)
        
        # Create frontend README
        readme_content = """# ZtionSec Frontend

Static frontend for ZtionSec security analysis platform.

## Deployment

This frontend is designed to be deployed on Netlify and connects to the ZtionSec API backend.

### Configuration

1. Update the API URL in `frontend/js/app.js`:
   ```javascript
   const API_BASE_URL = 'https://your-ztionsec-api.onrender.com/api/v1';
   ```

2. Deploy to Netlify:
   - Connect this repository to Netlify
   - Set build directory to `frontend`
   - Deploy automatically

### Features

- Responsive design with Bootstrap 5
- Real-time security scanning
- Multiple scan types (Basic, Advanced, Budget, P4)
- Data breach checking
- Scan history and analytics
- Modern UI with animations

### API Integration

The frontend communicates with the ZtionSec backend API for:
- Security scans
- Data breach checks
- Scan history
- Platform statistics

Make sure your backend API is deployed and accessible before using the frontend.
"""
        
        with open(self.frontend_dir / 'README.md', 'w') as f:
            f.write(readme_content)
        
        print("✅ Frontend deployment ready in frontend-deploy/")
        return True
    
    def update_api_urls(self, api_url):
        """Update API URLs in frontend"""
        js_file = self.frontend_dir / "frontend" / "js" / "app.js"
        
        if js_file.exists():
            with open(js_file, 'r') as f:
                content = f.read()
            
            # Replace API URL
            content = content.replace(
                "const API_BASE_URL = 'https://your-ztionsec-api.onrender.com/api/v1';",
                f"const API_BASE_URL = '{api_url}/api/v1';"
            )
            
            with open(js_file, 'w') as f:
                f.write(content)
            
            print(f"✅ Updated API URL to {api_url}")
    
    def create_deployment_instructions(self):
        """Create deployment instructions"""
        instructions = """# 🚀 ZtionSec Separated Deployment Instructions

## Backend Deployment (Render)

1. Create new repository for backend:
   ```bash
   cd backend-deploy
   git init
   git add .
   git commit -m "ZtionSec Backend API"
   git remote add origin https://github.com/yourusername/ztionsec-backend.git
   git push -u origin main
   ```

2. Deploy to Render:
   - Go to render.com
   - Create Web Service from GitHub repo
   - Use render.yaml configuration
   - Add PostgreSQL database

## Frontend Deployment (Netlify)

1. Create new repository for frontend:
   ```bash
   cd frontend-deploy
   git init
   git add .
   git commit -m "ZtionSec Frontend"
   git remote add origin https://github.com/yourusername/ztionsec-frontend.git
   git push -u origin main
   ```

2. Deploy to Netlify:
   - Go to netlify.com
   - Create site from GitHub repo
   - Set publish directory to 'frontend'
   - Deploy automatically

## Configuration

1. Update API URL in frontend/js/app.js with your Render backend URL
2. Update CORS settings in backend to allow your Netlify domain
3. Test the connection between frontend and backend

## URLs

- Backend API: https://your-app.onrender.com
- Frontend: https://your-site.netlify.app

Your ZtionSec platform is now ready for production! 🎉
"""
        
        with open(self.project_root / 'DEPLOYMENT_INSTRUCTIONS.md', 'w') as f:
            f.write(instructions)
        
        print("✅ Deployment instructions created")
    
    def run_deployment_prep(self):
        """Run complete deployment preparation"""
        print("🚀 ZtionSec Separated Architecture Deployment")
        print("=" * 50)
        
        # Create backend deployment
        if not self.create_backend_deployment():
            print("❌ Backend deployment preparation failed!")
            return False
        
        # Create frontend deployment
        if not self.create_frontend_deployment():
            print("❌ Frontend deployment preparation failed!")
            return False
        
        # Create instructions
        self.create_deployment_instructions()
        
        print("\n" + "=" * 50)
        print("✅ Deployment preparation complete!")
        print("\n📁 Created directories:")
        print(f"   🔧 Backend:  {self.backend_dir}")
        print(f"   🎨 Frontend: {self.frontend_dir}")
        
        print("\n📋 Next steps:")
        print("1. Create separate GitHub repositories for backend and frontend")
        print("2. Deploy backend to Render.com")
        print("3. Deploy frontend to Netlify")
        print("4. Update API URLs and CORS settings")
        print("5. Test the complete system")
        
        print("\n📖 See DEPLOYMENT_INSTRUCTIONS.md for detailed steps")
        
        return True

def main():
    deployment = SeparatedDeployment()
    
    # Get API URL if provided
    api_url = None
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
        print(f"🔗 Will configure frontend for API: {api_url}")
    
    # Run deployment preparation
    success = deployment.run_deployment_prep()
    
    # Update API URL if provided
    if success and api_url:
        deployment.update_api_urls(api_url)
    
    if success:
        print("\n🎉 Ready for separated deployment!")
        sys.exit(0)
    else:
        print("\n❌ Deployment preparation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
