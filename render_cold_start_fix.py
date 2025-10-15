#!/usr/bin/env python3
"""
Comprehensive Render Cold Start Fix
Addresses all common causes of cold start issues
"""

import os
import sys
import time
import requests
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RenderColdStartFix:
    def __init__(self):
        self.service_url = None
        self.health_endpoint = None
        
    def detect_service_url(self):
        """Auto-detect service URL from environment or config"""
        # Try to get from environment
        self.service_url = os.getenv('RENDER_EXTERNAL_URL')
        
        if not self.service_url:
            # Try to read from render.yaml
            try:
                with open('render.yaml', 'r') as f:
                    content = f.read()
                    # Extract service name
                    import re
                    match = re.search(r'name:\s*(\S+)', content)
                    if match:
                        service_name = match.group(1)
                        self.service_url = f"https://{service_name}.onrender.com"
            except:
                pass
        
        if not self.service_url:
            logger.error("❌ Could not detect service URL. Please set RENDER_EXTERNAL_URL environment variable")
            return False
        
        self.health_endpoint = f"{self.service_url}/api/v1/health/"
        logger.info(f"🎯 Detected service URL: {self.service_url}")
        return True
    
    def check_service_status(self):
        """Check current service status"""
        if not self.detect_service_url():
            return False
        
        logger.info("🏥 Checking service status...")
        
        try:
            response = requests.get(self.health_endpoint, timeout=30)
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Service is currently ACTIVE")
                logger.info(f"   Response time: {data.get('response_time_ms', 'N/A')}ms")
                logger.info(f"   Database: {data.get('database', 'unknown')}")
                return True
            else:
                logger.warning(f"⚠️ Service returned status {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            logger.error("❌ Service is SLEEPING (timeout)")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ Service is SLEEPING (connection error)")
            return False
        except Exception as e:
            logger.error(f"❌ Service check failed: {str(e)}")
            return False
    
    def wake_up_service(self):
        """Aggressively wake up sleeping service"""
        if not self.health_endpoint:
            return False
        
        logger.info("🔥 Attempting to wake up service...")
        
        endpoints = [
            self.health_endpoint,
            f"{self.service_url}/api/v1/stats/",
            f"{self.service_url}/api/v1/scan-history/",
        ]
        
        for attempt in range(10):  # 10 attempts
            logger.info(f"   Attempt {attempt + 1}/10")
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=45)
                    if response.status_code == 200:
                        logger.info(f"✅ Service woke up! ({endpoint})")
                        return True
                except:
                    pass
                time.sleep(2)
            
            time.sleep(5)  # Wait 5 seconds between attempts
        
        logger.error("❌ Failed to wake up service after 10 attempts")
        return False
    
    def setup_github_actions_keepalive(self):
        """Setup GitHub Actions for external keep-alive"""
        github_dir = Path('.github/workflows')
        github_dir.mkdir(parents=True, exist_ok=True)
        
        keepalive_yaml = """name: ZtionSec Keep-Alive

on:
  schedule:
    # Every 5 minutes
    - cron: '*/5 * * * *'
  workflow_dispatch:

jobs:
  keepalive:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Wake Up Service
        run: |
          echo "Pinging ZtionSec service..."
          
          # Multiple endpoint pinging
          ENDPOINTS=(
            "https://ztionsec-api.onrender.com/api/v1/health/"
            "https://ztionsec-api.onrender.com/api/v1/stats/"
          )
          
          for endpoint in "${ENDPOINTS[@]}"; do
            echo "Pinging: $endpoint"
            curl -f -m 30 "$endpoint" || echo "Failed to ping $endpoint"
            sleep 2
          done
          
          echo "Keep-alive completed"
        continue-on-error: true
"""
        
        keepalive_file = github_dir / 'keepalive.yml'
        with open(keepalive_file, 'w') as f:
            f.write(keepalive_yaml)
        
        logger.info(f"✅ Created GitHub Actions keep-alive: {keepalive_file}")
        return True
    
    def optimize_render_config(self):
        """Optimize render.yaml configuration"""
        render_config = """# Optimized Render.com configuration for cold start prevention
services:
  - type: web
    name: ztionsec-api
    env: python
    plan: free
    buildCommand: |
      pip install --upgrade pip
      pip install -r requirements.txt
      python manage.py collectstatic --noinput
      python manage.py migrate
    startCommand: |
      python manage.py migrate --run-syncdb
      gunicorn Ztionsec.wsgi:application --config gunicorn.conf.py --preload --max-requests 1000 --max-requests-jitter 50
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: Ztionsec.settings_deploy
      - key: DEBUG
        value: "False"
      - key: ALLOWED_HOSTS
        value: "*"
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: ztionsec-db
          property: connectionString
      - key: CORS_ALLOW_ALL_ORIGINS
        value: "True"
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: PYTHONDONTWRITEBYTECODE
        value: "1"
      - key: WEB_CONCURRENCY
        value: "2"
      - key: GUNICORN_TIMEOUT
        value: "120"
    healthCheckPath: /api/v1/health/
    
  - type: pserv
    name: ztionsec-db
    env: postgresql
    plan: free
    databaseName: ztionsec
    databaseUser: ztionsec
"""
        
        with open('render.yaml', 'w') as f:
            f.write(render_config)
        
        logger.info("✅ Optimized render.yaml configuration")
        return True
    
    def create_uptime_monitoring_script(self):
        """Create a simple uptime monitoring script"""
        monitor_script = """#!/bin/bash
# Simple uptime monitor for ZtionSec
# Run this on a VPS or local machine

SERVICE_URL="https://ztionsec-api.onrender.com"
HEALTH_ENDPOINT="$SERVICE_URL/api/v1/health/"

while true; do
    echo "$(date): Checking service..."
    
    if curl -f -m 30 "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
        echo "✅ Service is up"
    else
        echo "❌ Service is down - attempting to wake up..."
        
        # Try multiple endpoints
        curl -f -m 45 "$SERVICE_URL/api/v1/stats/" > /dev/null 2>&1
        curl -f -m 45 "$HEALTH_ENDPOINT" > /dev/null 2>&1
        
        sleep 30
        
        # Check again
        if curl -f -m 30 "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
            echo "✅ Service woke up"
        else
            echo "❌ Service still down"
        fi
    fi
    
    # Wait 5 minutes
    sleep 300
done
"""
        
        with open('uptime_monitor.sh', 'w') as f:
            f.write(monitor_script)
        
        os.chmod('uptime_monitor.sh', 0o755)
        logger.info("✅ Created uptime monitoring script: uptime_monitor.sh")
        return True
    
    def run_comprehensive_fix(self):
        """Run all cold start fixes"""
        logger.info("🚀 Starting Comprehensive Cold Start Fix")
        logger.info("=" * 60)
        
        # Step 1: Check current status
        logger.info("Step 1: Checking service status...")
        is_active = self.check_service_status()
        
        if not is_active:
            # Step 2: Try to wake up service
            logger.info("Step 2: Attempting to wake up service...")
            self.wake_up_service()
        
        # Step 3: Setup external monitoring
        logger.info("Step 3: Setting up GitHub Actions keep-alive...")
        self.setup_github_actions_keepalive()
        
        # Step 4: Optimize configuration
        logger.info("Step 4: Optimizing Render configuration...")
        self.optimize_render_config()
        
        # Step 5: Create monitoring tools
        logger.info("Step 5: Creating monitoring tools...")
        self.create_uptime_monitoring_script()
        
        logger.info("=" * 60)
        logger.info("🎉 Comprehensive cold start fix completed!")
        
        # Final recommendations
        logger.info("\n📋 NEXT STEPS:")
        logger.info("1. Commit and push the updated render.yaml")
        logger.info("2. Enable GitHub Actions in your repository")
        logger.info("3. Consider running uptime_monitor.sh on a VPS")
        logger.info("4. Monitor your service for the next few hours")
        
        return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Render Cold Start Fix')
    parser.add_argument('--check', action='store_true', help='Only check service status')
    parser.add_argument('--wake', action='store_true', help='Only wake up service')
    parser.add_argument('--setup', action='store_true', help='Only setup monitoring')
    
    args = parser.parse_args()
    
    fixer = RenderColdStartFix()
    
    if args.check:
        fixer.check_service_status()
    elif args.wake:
        fixer.wake_up_service()
    elif args.setup:
        fixer.setup_github_actions_keepalive()
        fixer.create_uptime_monitoring_script()
    else:
        fixer.run_comprehensive_fix()

if __name__ == "__main__":
    main()
