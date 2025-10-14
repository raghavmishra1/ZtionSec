#!/usr/bin/env python3
"""
Update existing scan scores with improved algorithm
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append('/home/offensive/Desktop/Ztionsec')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ztionsec.settings')
django.setup()

from scanner.models import SecurityScan
from scanner.utils import SecurityScanner

def update_scan_scores():
    """Update scores for existing scans"""
    scans = SecurityScan.objects.all()
    updated_count = 0
    
    print(f"Found {scans.count()} scans to update...")
    
    for scan in scans:
        try:
            # Create a results dict from the scan data
            results = {
                'status_code': scan.status_code or 200,
                'ssl_valid': scan.ssl_valid,
                'ssl_grade': scan.ssl_grade or 'F',
                'has_hsts': scan.has_hsts,
                'has_csp': scan.has_csp,
                'has_xframe': scan.has_xframe,
                'has_xss_protection': scan.has_xss_protection,
                'has_content_type': scan.has_content_type,
                'response_time': scan.response_time or 1000,
            }
            
            # Create a temporary scanner to calculate score
            scanner = SecurityScanner(scan.url)
            score, grade = scanner.calculate_security_score(results)
            
            # Update the scan
            scan.security_score = score
            scan.grade = grade
            scan.save()
            
            print(f"Updated {scan.url}: {score}/100 ({grade})")
            updated_count += 1
            
        except Exception as e:
            print(f"Error updating {scan.url}: {e}")
    
    print(f"\nUpdated {updated_count} scans successfully!")

if __name__ == "__main__":
    update_scan_scores()
