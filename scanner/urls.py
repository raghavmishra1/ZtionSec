from django.urls import path
from . import views, advanced_views

urlpatterns = [
    path('', views.home, name='home'),
    path('scan/', views.scan_website, name='scan_website'),
    path('breach/', views.check_breach, name='check_breach'),
    path('api/scan/', views.api_scan, name='api_scan'),
    path('generate-report/<int:scan_id>/', views.generate_report, name='generate_report'),
    path('history/', views.scan_history, name='scan_history'),
    path('breach-history/', views.breach_history, name='breach_history'),
    
    # Advanced scanning URLs
    path('advanced/', advanced_views.advanced_scan_dashboard, name='advanced_dashboard'),
    path('advanced/scan/', advanced_views.start_advanced_scan, name='advanced_scan'),
    path('advanced/results/<int:scan_id>/', advanced_views.advanced_scan_results, name='advanced_scan_results'),
    path('advanced/history/', advanced_views.advanced_scan_history, name='advanced_scan_history'),
    path('advanced/report/<int:scan_id>/', advanced_views.generate_advanced_report, name='generate_advanced_report'),
    path('advanced/analytics/', advanced_views.security_analytics, name='security_analytics'),
    path('api/advanced-scan/', advanced_views.api_advanced_scan, name='api_advanced_scan'),
    path('api/analytics-data/', advanced_views.analytics_api_data, name='analytics_api_data'),
    
    # Intelligence URLs
    path('vulnerabilities/', advanced_views.vulnerability_database_view, name='vulnerability_database'),
    path('threat-intel/', advanced_views.threat_intelligence_view, name='threat_intelligence'),
    path('configurations/', advanced_views.scan_configurations, name='scan_configurations'),
    path('p4-scanner/', advanced_views.p4_security_scan, name='p4_security_scan'),
    
    # New pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('budget-scanner/', views.budget_scanner, name='budget_scanner'),
    path('budget-scan/', views.budget_scan, name='budget_scan'),
    path('budget-results/', views.budget_results, name='budget_results'),
    
    # Test pages
    path('modal-test/', views.modal_test, name='modal_test'),
]
