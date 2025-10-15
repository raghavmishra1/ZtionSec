from django.core.management.base import BaseCommand
from django.utils import timezone
from scanner.models import SecurityScan
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Create sample security scan data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of sample scans to create',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Sample websites with realistic data
        sample_data = [
            {
                'url': 'https://www.google.com',
                'ssl_valid': True,
                'ssl_issuer': 'Google Trust Services',
                'ssl_grade': 'A+',
                'has_hsts': True,
                'has_csp': True,
                'has_xframe': True,
                'has_xss_protection': True,
                'has_content_type': True,
                'cms_detected': 'Custom',
                'response_time': random.uniform(100, 300),
                'status_code': 200,
                'security_score': random.randint(85, 95),
                'grade': 'A+',
                'server_info': 'gws',
            },
            {
                'url': 'https://github.com',
                'ssl_valid': True,
                'ssl_issuer': 'DigiCert Inc',
                'ssl_grade': 'A',
                'has_hsts': True,
                'has_csp': True,
                'has_xframe': True,
                'has_xss_protection': True,
                'has_content_type': True,
                'cms_detected': 'Ruby on Rails',
                'response_time': random.uniform(200, 500),
                'status_code': 200,
                'security_score': random.randint(80, 90),
                'grade': 'A',
                'server_info': 'GitHub.com',
            },
            {
                'url': 'https://stackoverflow.com',
                'ssl_valid': True,
                'ssl_issuer': 'Cloudflare Inc',
                'ssl_grade': 'A',
                'has_hsts': True,
                'has_csp': False,
                'has_xframe': True,
                'has_xss_protection': True,
                'has_content_type': True,
                'cms_detected': 'ASP.NET',
                'response_time': random.uniform(150, 400),
                'status_code': 200,
                'security_score': random.randint(75, 85),
                'grade': 'B+',
                'server_info': 'cloudflare',
            },
            {
                'url': 'https://www.reddit.com',
                'ssl_valid': True,
                'ssl_issuer': 'Amazon',
                'ssl_grade': 'A',
                'has_hsts': True,
                'has_csp': True,
                'has_xframe': False,
                'has_xss_protection': True,
                'has_content_type': True,
                'cms_detected': 'React',
                'response_time': random.uniform(300, 600),
                'status_code': 200,
                'security_score': random.randint(70, 80),
                'grade': 'B',
                'server_info': 'snooserv',
            },
            {
                'url': 'https://www.wikipedia.org',
                'ssl_valid': True,
                'ssl_issuer': 'GlobalSign',
                'ssl_grade': 'A+',
                'has_hsts': True,
                'has_csp': True,
                'has_xframe': True,
                'has_xss_protection': True,
                'has_content_type': True,
                'cms_detected': 'MediaWiki',
                'response_time': random.uniform(200, 400),
                'status_code': 200,
                'security_score': random.randint(85, 95),
                'grade': 'A',
                'server_info': 'mw-web',
            },
            {
                'url': 'http://example.com',
                'ssl_valid': False,
                'ssl_issuer': '',
                'ssl_grade': 'F',
                'has_hsts': False,
                'has_csp': False,
                'has_xframe': False,
                'has_xss_protection': False,
                'has_content_type': True,
                'cms_detected': 'Apache',
                'response_time': random.uniform(500, 1000),
                'status_code': 200,
                'security_score': random.randint(20, 40),
                'grade': 'F',
                'server_info': 'Apache/2.4.41',
            },
            {
                'url': 'https://www.cloudflare.com',
                'ssl_valid': True,
                'ssl_issuer': 'Cloudflare Inc',
                'ssl_grade': 'A+',
                'has_hsts': True,
                'has_csp': True,
                'has_xframe': True,
                'has_xss_protection': True,
                'has_content_type': True,
                'cms_detected': 'Next.js',
                'response_time': random.uniform(100, 250),
                'status_code': 200,
                'security_score': random.randint(90, 100),
                'grade': 'A+',
                'server_info': 'cloudflare',
            },
        ]
        
        created_count = 0
        
        for i in range(count):
            # Select random sample data
            sample = random.choice(sample_data)
            
            # Create scan with some variation
            scan_date = timezone.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Add some randomness to the data
            security_score = sample['security_score'] + random.randint(-5, 5)
            security_score = max(0, min(100, security_score))  # Clamp between 0-100
            
            response_time = sample['response_time'] + random.uniform(-50, 100)
            response_time = max(50, response_time)  # Minimum 50ms
            
            scan = SecurityScan.objects.create(
                url=sample['url'],
                scan_date=scan_date,
                ssl_valid=sample['ssl_valid'],
                ssl_issuer=sample['ssl_issuer'],
                ssl_grade=sample['ssl_grade'],
                has_hsts=sample['has_hsts'],
                has_csp=sample['has_csp'],
                has_xframe=sample['has_xframe'],
                has_xss_protection=sample['has_xss_protection'],
                has_content_type=sample['has_content_type'],
                cms_detected=sample['cms_detected'],
                response_time=round(response_time, 2),
                status_code=sample['status_code'],
                security_score=security_score,
                grade=sample['grade'],
                server_info=sample['server_info'],
                technologies=f"SSL/TLS, HTTP/2, {sample['cms_detected']}",
            )
            
            created_count += 1
            
            if created_count % 5 == 0:
                self.stdout.write(f'Created {created_count} scans...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} sample security scans!'
            )
        )
        
        # Show statistics
        total_scans = SecurityScan.objects.count()
        ssl_secured = SecurityScan.objects.filter(ssl_valid=True).count()
        grade_a = SecurityScan.objects.filter(grade__in=['A+', 'A']).count()
        
        self.stdout.write(f'\nCurrent Statistics:')
        self.stdout.write(f'Total Scans: {total_scans}')
        self.stdout.write(f'SSL Secured: {ssl_secured}')
        self.stdout.write(f'Grade A+/A: {grade_a}')
