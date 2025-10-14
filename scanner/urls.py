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
    
    # Resource pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('documentation/', views.documentation, name='documentation'),
    path('tutorials/', views.tutorials, name='tutorials'),
    path('faq/', views.faq, name='faq'),
    
    # Enterprise pages
    path('enterprise/', views.enterprise, name='enterprise'),
    path('api-access/', views.api_access, name='api_access'),
    path('team-plans/', views.team_plans, name='team_plans'),
    path('partnerships/', views.partnerships, name='partnerships'),
    
    # Scanner pages
    path('budget-scanner/', views.budget_scanner, name='budget_scanner'),
    path('budget-scan/', views.budget_scan, name='budget_scan'),
    path('budget-results/', views.budget_results, name='budget_results'),
    path('budget-clear/', views.budget_clear_results, name='budget_clear_results'),
    path('breach-check/', views.breach_check_page, name='breach_check'),
    path('cve-database/', views.cve_database, name='cve_database'),
    
    # Newsletter and updates
    path('newsletter/', views.newsletter_signup, name='newsletter_signup'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # Test pages
    path('modal-test/', views.modal_test, name='modal_test'),
    
    # Quick scan
    path('quick-scan/', views.quick_scan, name='quick_scan'),
    
    # Health checks for production
    path('health/', views.health_check, name='health_check'),
    path('api/v1/health/', views.api_health_check, name='api_health_check'),
]
