#!/usr/bin/env python3
"""
ZtionSec Free Hosting Deployment Script
Automates deployment preparation for free hosting platforms
"""

import os
import sys
import subprocess
import json
import secrets
import string

class DeploymentHelper:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.platforms = {
            'render': 'Render.com',
            'railway': 'Railway.app', 
            'pythonanywhere': 'PythonAnywhere',
            'heroku': 'Heroku'
        }
    
    def generate_secret_key(self):
        """Generate a secure Django secret key"""
        chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
        return ''.join(secrets.choice(chars) for _ in range(50))
    
    def create_env_file(self, platform='render'):
        """Create environment file for deployment"""
        secret_key = self.generate_secret_key()
        
        env_content = f"""# ZtionSec Production Environment Variables
# Generated for {self.platforms.get(platform, platform)} deployment

# Core Django Settings
DEBUG=False
SECRET_KEY={secret_key}
DJANGO_SETTINGS_MODULE=Ztionsec.settings_deploy
ALLOWED_HOSTS=*

# Database (will be auto-configured by hosting platform)
# DATABASE_URL=postgresql://user:password@host:port/dbname

# Security Settings
SECURE_SSL_REDIRECT=True

# API Keys (Optional - add your keys here)
HAVEIBEENPWNED_API_KEY=
SHODAN_API_KEY=
CENSYS_API_ID=
CENSYS_API_SECRET=

# Rate Limiting (Adjusted for free hosting)
RATE_LIMIT_SCANS_PER_HOUR=5
RATE_LIMIT_API_CALLS_PER_HOUR=50
ENABLE_PORT_SCANNING=False
ENABLE_ADVANCED_SCANNING=True
ENABLE_VULNERABILITY_SCANNING=True

# Platform-specific settings
PYTHON_VERSION=3.11.9
"""
        
        env_file = os.path.join(self.project_root, '.env.production')
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Created {env_file}")
        print(f"🔑 Generated secure secret key")
        return env_file
    
    def check_requirements(self):
        """Check if all required files exist"""
        required_files = [
            'requirements.txt',
            'manage.py',
            'Ztionsec/settings.py',
            'Ztionsec/settings_deploy.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(self.project_root, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            print("❌ Missing required files:")
            for file_path in missing_files:
                print(f"   - {file_path}")
            return False
        
        print("✅ All required files present")
        return True
    
    def setup_git_repository(self):
        """Initialize git repository if not exists"""
        git_dir = os.path.join(self.project_root, '.git')
        
        if not os.path.exists(git_dir):
            print("📦 Initializing git repository...")
            try:
                subprocess.run(['git', 'init'], cwd=self.project_root, check=True)
                subprocess.run(['git', 'add', '.'], cwd=self.project_root, check=True)
                subprocess.run(['git', 'commit', '-m', 'Initial ZtionSec deployment'], 
                             cwd=self.project_root, check=True)
                print("✅ Git repository initialized")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Git setup failed: {e}")
                return False
        else:
            print("✅ Git repository already exists")
            return True
    
    def test_django_setup(self):
        """Test Django configuration"""
        print("🧪 Testing Django configuration...")
        
        try:
            # Test settings import
            os.environ['DJANGO_SETTINGS_MODULE'] = 'Ztionsec.settings_deploy'
            
            # Run Django checks
            result = subprocess.run([
                sys.executable, 'manage.py', 'check', '--deploy'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Django configuration is valid")
                return True
            else:
                print("❌ Django configuration issues:")
                print(result.stdout)
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Django test failed: {e}")
            return False
    
    def create_platform_instructions(self, platform):
        """Create platform-specific deployment instructions"""
        instructions = {
            'render': """
🚀 Render.com Deployment Instructions:

1. Push your code to GitHub:
   git remote add origin https://github.com/yourusername/ztionsec.git
   git push -u origin main

2. Go to render.com and create account
3. Create new Web Service from GitHub repo
4. Configure:
   - Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   - Start Command: gunicorn Ztionsec.wsgi:application
   - Environment Variables: Copy from .env.production

5. Create PostgreSQL database and connect to web service
6. Deploy and test!

Your app will be available at: https://ztionsec.onrender.com
""",
            'railway': """
🚀 Railway.app Deployment Instructions:

1. Push your code to GitHub:
   git remote add origin https://github.com/yourusername/ztionsec.git
   git push -u origin main

2. Go to railway.app and create account
3. Create new project from GitHub repo
4. Add PostgreSQL database
5. Set environment variables from .env.production
6. Deploy automatically!

Your app will be available at: https://ztionsec.up.railway.app
""",
            'pythonanywhere': """
🚀 PythonAnywhere Deployment Instructions:

1. Create account at pythonanywhere.com
2. Open Bash console and clone repo:
   git clone https://github.com/yourusername/ztionsec.git
   cd ztionsec

3. Create virtual environment:
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

4. Create web app in Web tab (Manual configuration)
5. Configure WSGI file and static files
6. Set environment variables in Web tab

Your app will be available at: https://yourusername.pythonanywhere.com
"""
        }
        
        return instructions.get(platform, "Platform instructions not available")
    
    def deploy_preparation(self, platform='render'):
        """Complete deployment preparation"""
        print(f"🚀 Preparing ZtionSec for {self.platforms.get(platform, platform)} deployment...")
        print("=" * 60)
        
        # Check requirements
        if not self.check_requirements():
            return False
        
        # Create environment file
        self.create_env_file(platform)
        
        # Setup git
        if not self.setup_git_repository():
            return False
        
        # Test Django
        if not self.test_django_setup():
            print("⚠️  Django configuration has issues, but proceeding...")
        
        print("\n" + "=" * 60)
        print("✅ Deployment preparation complete!")
        print("\n📋 Next Steps:")
        print(self.create_platform_instructions(platform))
        
        print("\n🔧 Important Notes:")
        print("- Update .env.production with your actual API keys")
        print("- Replace placeholder URLs with your actual domain")
        print("- Test the deployment thoroughly")
        print("- Set up monitoring using the monitoring/ directory")
        
        return True

def main():
    helper = DeploymentHelper()
    
    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
        if platform not in helper.platforms:
            print(f"❌ Unknown platform: {platform}")
            print(f"Available platforms: {', '.join(helper.platforms.keys())}")
            sys.exit(1)
    else:
        platform = 'render'  # Default platform
    
    print(f"🎯 Target platform: {helper.platforms[platform]}")
    
    success = helper.deploy_preparation(platform)
    
    if success:
        print("\n🎉 Ready for deployment!")
        sys.exit(0)
    else:
        print("\n❌ Deployment preparation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
