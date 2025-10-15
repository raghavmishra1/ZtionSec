#!/usr/bin/env python3
"""
Startup Optimization Script for ZtionSec
Performs pre-warming and optimization tasks to reduce cold start time
"""

import os
import sys
import django
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_django():
    """Setup Django environment"""
    # Add the project directory to Python path
    project_dir = Path(__file__).parent
    sys.path.insert(0, str(project_dir))
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ztionsec.settings_deploy')
    django.setup()

def pre_warm_database():
    """Pre-warm database connections"""
    logger.info("🔥 Pre-warming database connections...")
    
    try:
        from django.db import connection
        from scanner.models import SecurityScan, AdvancedSecurityScan
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Pre-load some model metadata
        SecurityScan._meta.get_fields()
        AdvancedSecurityScan._meta.get_fields()
        
        logger.info("✅ Database pre-warming completed")
        return True
    except Exception as e:
        logger.error(f"❌ Database pre-warming failed: {str(e)}")
        return False

def pre_load_modules():
    """Pre-load commonly used modules"""
    logger.info("📦 Pre-loading modules...")
    
    try:
        # Import commonly used modules to cache them
        import requests
        import json
        import ssl
        import socket
        import urllib.parse
        from rest_framework.response import Response
        from django.http import JsonResponse
        
        # Import scanner modules
        from scanner.advanced_scanner import AdvancedSecurityScanner
        from scanner.budget_scanner import BudgetSecurityScanner
        
        logger.info("✅ Module pre-loading completed")
        return True
    except Exception as e:
        logger.error(f"❌ Module pre-loading failed: {str(e)}")
        return False

def optimize_static_files():
    """Optimize static file serving"""
    logger.info("📁 Optimizing static files...")
    
    try:
        from django.core.management import call_command
        from django.conf import settings
        
        # Ensure static files are collected
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            static_root = Path(settings.STATIC_ROOT)
            if not static_root.exists() or not any(static_root.iterdir()):
                logger.info("Collecting static files...")
                call_command('collectstatic', '--noinput', verbosity=0)
        
        logger.info("✅ Static files optimization completed")
        return True
    except Exception as e:
        logger.error(f"❌ Static files optimization failed: {str(e)}")
        return False

def run_health_check():
    """Run internal health check"""
    logger.info("🏥 Running health check...")
    
    try:
        from scanner.api_views import api_health_check
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/api/v1/health/')
        
        response = api_health_check(request)
        
        if response.status_code == 200:
            logger.info("✅ Health check passed")
            return True
        else:
            logger.error(f"❌ Health check failed with status: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return False

def create_cache_directories():
    """Create necessary cache directories"""
    logger.info("📂 Creating cache directories...")
    
    try:
        from django.conf import settings
        
        # Create media directory
        if hasattr(settings, 'MEDIA_ROOT'):
            media_root = Path(settings.MEDIA_ROOT)
            media_root.mkdir(exist_ok=True)
            
        # Create cache directories
        cache_dirs = ['cache', 'tmp', 'logs']
        for cache_dir in cache_dirs:
            Path(cache_dir).mkdir(exist_ok=True)
        
        logger.info("✅ Cache directories created")
        return True
    except Exception as e:
        logger.error(f"❌ Cache directory creation failed: {str(e)}")
        return False

def main():
    """Main optimization function"""
    start_time = time.time()
    logger.info("🚀 Starting ZtionSec startup optimization...")
    
    # Setup Django
    setup_django()
    
    # Run optimization tasks
    tasks = [
        ("Database Pre-warming", pre_warm_database),
        ("Module Pre-loading", pre_load_modules),
        ("Static Files Optimization", optimize_static_files),
        ("Cache Directories", create_cache_directories),
        ("Health Check", run_health_check),
    ]
    
    results = {}
    for task_name, task_func in tasks:
        logger.info(f"Running: {task_name}")
        results[task_name] = task_func()
    
    # Summary
    total_time = time.time() - start_time
    successful_tasks = sum(results.values())
    total_tasks = len(results)
    
    logger.info("=" * 50)
    logger.info(f"🎯 Optimization Summary:")
    logger.info(f"   ✅ Successful tasks: {successful_tasks}/{total_tasks}")
    logger.info(f"   ⏱️  Total time: {total_time:.2f} seconds")
    
    if successful_tasks == total_tasks:
        logger.info("🎉 All optimization tasks completed successfully!")
        return 0
    else:
        logger.warning("⚠️ Some optimization tasks failed")
        return 1

if __name__ == "__main__":
    exit(main())
