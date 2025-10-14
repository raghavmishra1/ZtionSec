"""
API URLs for ZtionSec REST API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# API URL patterns
api_urlpatterns = [
    # Health and status
    path('health/', api_views.api_health_check, name='api_health'),
    path('stats/', api_views.api_stats, name='api_stats'),
    
    # Scanning endpoints
    path('scan/basic/', api_views.api_basic_scan, name='api_basic_scan'),
    path('scan/advanced/', api_views.api_advanced_scan, name='api_advanced_scan'),
    path('scan/budget/', api_views.api_budget_scan, name='api_budget_scan'),
    path('scan/p4/', api_views.api_p4_scan, name='api_p4_scan'),
    
    # Data breach checking
    path('breach/check/', api_views.api_breach_check, name='api_breach_check'),
    
    # Scan history and details
    path('scans/history/', api_views.api_scan_history, name='api_scan_history'),
    path('scans/<int:scan_id>/', api_views.api_scan_details, name='api_scan_details'),
    
    # CORS support
    path('options/', api_views.api_options, name='api_options'),
]

urlpatterns = [
    path('api/v1/', include(api_urlpatterns)),
]
