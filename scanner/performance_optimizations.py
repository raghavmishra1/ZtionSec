"""
Performance Optimizations for ZtionSec
Senior Developer Implementation - Database & Caching
"""

from django.db import models
from django.core.cache import cache
from django.conf import settings
import hashlib
import json
from functools import wraps
from datetime import timedelta
from django.utils import timezone

class CacheManager:
    """Advanced caching manager for ZtionSec"""
    
    CACHE_TIMEOUTS = {
        'scan_results': 3600,  # 1 hour
        'breach_check': 86400,  # 24 hours
        'vulnerability_data': 43200,  # 12 hours
        'dns_lookup': 1800,  # 30 minutes
        'ssl_check': 7200,  # 2 hours
    }
    
    @staticmethod
    def generate_cache_key(prefix, *args, **kwargs):
        """Generate consistent cache key"""
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        if kwargs:
            key_data += f":{json.dumps(kwargs, sort_keys=True)}"
        
        # Hash long keys
        if len(key_data) > 200:
            key_data = hashlib.md5(key_data.encode()).hexdigest()
        
        return key_data
    
    @classmethod
    def get_cached_result(cls, cache_type, *args, **kwargs):
        """Get cached result"""
        cache_key = cls.generate_cache_key(cache_type, *args, **kwargs)
        return cache.get(cache_key)
    
    @classmethod
    def set_cached_result(cls, cache_type, result, *args, **kwargs):
        """Set cached result"""
        cache_key = cls.generate_cache_key(cache_type, *args, **kwargs)
        timeout = cls.CACHE_TIMEOUTS.get(cache_type, 3600)
        cache.set(cache_key, result, timeout)
        return cache_key
    
    @classmethod
    def invalidate_cache(cls, cache_type, *args, **kwargs):
        """Invalidate specific cache"""
        cache_key = cls.generate_cache_key(cache_type, *args, **kwargs)
        cache.delete(cache_key)

def cache_result(cache_type, timeout=None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = CacheManager.generate_cache_key(
                f"{cache_type}:{func.__name__}", *args, **kwargs
            )
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_timeout = timeout or CacheManager.CACHE_TIMEOUTS.get(cache_type, 3600)
            cache.set(cache_key, result, cache_timeout)
            
            return result
        return wrapper
    return decorator

class DatabaseOptimizations:
    """Database optimization utilities"""
    
    @staticmethod
    def add_database_indexes():
        """Add database indexes for better performance"""
        from django.db import connection
        
        indexes = [
            # SecurityScan indexes
            "CREATE INDEX IF NOT EXISTS idx_security_scan_url ON scanner_securityscan(url);",
            "CREATE INDEX IF NOT EXISTS idx_security_scan_date ON scanner_securityscan(scan_date);",
            "CREATE INDEX IF NOT EXISTS idx_security_scan_score ON scanner_securityscan(security_score);",
            "CREATE INDEX IF NOT EXISTS idx_security_scan_grade ON scanner_securityscan(grade);",
            
            # AdvancedSecurityScan indexes
            "CREATE INDEX IF NOT EXISTS idx_advanced_scan_domain ON scanner_advancedsecurityscan(domain);",
            "CREATE INDEX IF NOT EXISTS idx_advanced_scan_risk ON scanner_advancedsecurityscan(risk_level);",
            "CREATE INDEX IF NOT EXISTS idx_advanced_scan_date ON scanner_advancedsecurityscan(scan_date);",
            
            # SecurityFinding indexes
            "CREATE INDEX IF NOT EXISTS idx_finding_severity ON scanner_securityfinding(severity);",
            "CREATE INDEX IF NOT EXISTS idx_finding_category ON scanner_securityfinding(category);",
            "CREATE INDEX IF NOT EXISTS idx_finding_cvss ON scanner_securityfinding(cvss_score);",
            
            # DataBreachCheck indexes
            "CREATE INDEX IF NOT EXISTS idx_breach_email ON scanner_databreachcheck(email);",
            "CREATE INDEX IF NOT EXISTS idx_breach_date ON scanner_databreachcheck(check_date);",
            
            # Composite indexes
            "CREATE INDEX IF NOT EXISTS idx_scan_url_date ON scanner_securityscan(url, scan_date);",
            "CREATE INDEX IF NOT EXISTS idx_finding_scan_severity ON scanner_securityfinding(scan_id, severity);",
        ]
        
        with connection.cursor() as cursor:
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                except Exception as e:
                    print(f"Index creation failed: {e}")
    
    @staticmethod
    def optimize_queries():
        """Optimize common database queries"""
        from scanner.models import SecurityScan, AdvancedSecurityScan, SecurityFinding
        
        # Prefetch related data to avoid N+1 queries
        def get_scans_with_findings():
            return AdvancedSecurityScan.objects.select_related().prefetch_related(
                'findings', 'reports'
            ).all()
        
        def get_recent_scans_optimized(limit=10):
            return SecurityScan.objects.select_related().only(
                'url', 'scan_date', 'security_score', 'grade', 'ssl_grade'
            )[:limit]
        
        def get_findings_by_severity():
            return SecurityFinding.objects.select_related('scan').values(
                'severity'
            ).annotate(
                count=models.Count('id')
            ).order_by('-count')
        
        return {
            'get_scans_with_findings': get_scans_with_findings,
            'get_recent_scans_optimized': get_recent_scans_optimized,
            'get_findings_by_severity': get_findings_by_severity,
        }

class PerformanceMiddleware:
    """Middleware for performance monitoring and optimization"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Start timing
        start_time = timezone.now()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate response time
        end_time = timezone.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        # Add performance headers
        response['X-Response-Time'] = f"{response_time:.2f}ms"
        
        # Log slow requests
        if response_time > 1000:  # Log requests slower than 1 second
            import logging
            logger = logging.getLogger('performance')
            logger.warning(
                f"Slow request: {request.method} {request.path} - {response_time:.2f}ms"
            )
        
        return response

class QueryOptimizer:
    """Query optimization utilities"""
    
    @staticmethod
    def bulk_create_findings(scan, findings_data):
        """Bulk create security findings for better performance"""
        from scanner.models import SecurityFinding
        
        findings = [
            SecurityFinding(
                scan=scan,
                severity=finding['severity'],
                category=finding['category'],
                title=finding['title'],
                description=finding['description'],
                recommendation=finding['recommendation'],
                cvss_score=finding.get('cvss_score'),
                cve_id=finding.get('cve_id'),
                affected_component=finding.get('affected_component', ''),
                proof_of_concept=finding.get('proof_of_concept', ''),
                references=finding.get('references', [])
            )
            for finding in findings_data
        ]
        
        SecurityFinding.objects.bulk_create(findings, batch_size=100)
    
    @staticmethod
    def update_scan_statistics():
        """Update scan statistics efficiently"""
        from scanner.models import AdvancedSecurityScan, SecurityFinding
        from django.db.models import Count, Avg
        
        # Use aggregation instead of individual queries
        stats = AdvancedSecurityScan.objects.aggregate(
            total_scans=Count('id'),
            avg_security_score=Avg('security_score'),
            critical_findings=Count('findings', filter=models.Q(findings__severity='critical')),
            high_findings=Count('findings', filter=models.Q(findings__severity='high')),
        )
        
        return stats
    
    @staticmethod
    def get_dashboard_data_optimized():
        """Get dashboard data with optimized queries"""
        from scanner.models import SecurityScan, DataBreachCheck
        from django.db.models import Count, Avg, Q
        from django.utils import timezone
        from datetime import timedelta
        
        # Use single query with aggregation
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        dashboard_data = SecurityScan.objects.aggregate(
            total_scans=Count('id'),
            scans_today=Count('id', filter=Q(scan_date__date=today)),
            scans_this_week=Count('id', filter=Q(scan_date__date__gte=week_ago)),
            avg_security_score=Avg('security_score'),
            high_security_sites=Count('id', filter=Q(security_score__gte=80)),
            low_security_sites=Count('id', filter=Q(security_score__lt=50)),
        )
        
        # Add breach check stats
        breach_stats = DataBreachCheck.objects.aggregate(
            total_checks=Count('id'),
            compromised_emails=Count('id', filter=Q(breaches_found__gt=0)),
        )
        
        dashboard_data.update(breach_stats)
        return dashboard_data

# Performance monitoring decorators
def monitor_performance(func_name=None):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = timezone.now()
            
            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
                raise
            finally:
                end_time = timezone.now()
                execution_time = (end_time - start_time).total_seconds() * 1000
                
                # Log performance metrics
                import logging
                logger = logging.getLogger('performance')
                
                name = func_name or f"{func.__module__}.{func.__name__}"
                logger.info(
                    f"Performance: {name} - {execution_time:.2f}ms - "
                    f"Success: {success} - Error: {error}"
                )
            
            return result
        return wrapper
    return decorator

# Cache warming utilities
class CacheWarmer:
    """Utilities for warming up caches"""
    
    @staticmethod
    def warm_dashboard_cache():
        """Warm up dashboard cache"""
        from scanner.views import home
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/')
        
        # This will populate the cache
        response = home(request)
        return response.status_code == 200
    
    @staticmethod
    def warm_scan_history_cache():
        """Warm up scan history cache"""
        from scanner.models import SecurityScan
        
        # Cache recent scans
        recent_scans = list(SecurityScan.objects.order_by('-scan_date')[:20])
        
        cache_key = CacheManager.generate_cache_key('recent_scans')
        cache.set(cache_key, recent_scans, 1800)  # 30 minutes
        
        return len(recent_scans)

# Database connection pooling (for production)
DATABASE_POOL_SETTINGS = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
            'sslmode': 'require',
        },
    }
}

# Redis configuration for caching
REDIS_CACHE_SETTINGS = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'KEY_PREFIX': 'ztionsec',
        'TIMEOUT': 300,
    }
}
