from django.contrib import admin
from .models import (
    SecurityScan, DataBreachCheck, AdvancedSecurityScan, SecurityFinding,
    VulnerabilityDatabase, ThreatIntelligence, ScanReport, ScanConfiguration
)

@admin.register(SecurityScan)
class SecurityScanAdmin(admin.ModelAdmin):
    list_display = ['url', 'grade', 'security_score', 'ssl_valid', 'scan_date']
    list_filter = ['grade', 'ssl_valid', 'has_hsts', 'has_csp', 'scan_date']
    search_fields = ['url', 'cms_detected']
    readonly_fields = ['scan_date']
    ordering = ['-scan_date']

@admin.register(AdvancedSecurityScan)
class AdvancedSecurityScanAdmin(admin.ModelAdmin):
    list_display = ['url', 'domain', 'risk_level', 'security_score', 'total_findings', 'scan_date']
    list_filter = ['risk_level', 'scan_date']
    search_fields = ['url', 'domain', 'ip_address']
    readonly_fields = ['scan_date', 'scan_duration']
    ordering = ['-scan_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('url', 'domain', 'ip_address', 'scan_date', 'scan_duration')
        }),
        ('Assessment Results', {
            'fields': ('security_score', 'risk_level', 'total_findings', 
                      'critical_findings', 'high_findings', 'medium_findings', 
                      'low_findings', 'info_findings')
        }),
        ('Scan Data', {
            'fields': ('dns_analysis', 'ssl_analysis', 'port_scan_results',
                      'webapp_scan_results', 'vulnerability_results', 
                      'subdomain_results', 'technology_stack', 
                      'security_headers', 'threat_intelligence'),
            'classes': ('collapse',)
        })
    )

@admin.register(SecurityFinding)
class SecurityFindingAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'category', 'scan', 'cve_id', 'cvss_score', 'created_date']
    list_filter = ['severity', 'category', 'created_date']
    search_fields = ['title', 'description', 'cve_id', 'scan__url']
    readonly_fields = ['created_date']
    ordering = ['-severity', '-cvss_score', '-created_date']
    
    fieldsets = (
        ('Finding Information', {
            'fields': ('scan', 'severity', 'category', 'title', 'description', 'recommendation')
        }),
        ('Vulnerability Details', {
            'fields': ('cve_id', 'cvss_score', 'affected_component', 'proof_of_concept', 'references')
        }),
        ('Metadata', {
            'fields': ('created_date',)
        })
    )

@admin.register(VulnerabilityDatabase)
class VulnerabilityDatabaseAdmin(admin.ModelAdmin):
    list_display = ['cve_id', 'cvss_score', 'severity', 'published_date', 'cached_date']
    list_filter = ['severity', 'published_date', 'cached_date']
    search_fields = ['cve_id', 'description']
    readonly_fields = ['cached_date']
    ordering = ['-cvss_score', '-published_date']

@admin.register(ThreatIntelligence)
class ThreatIntelligenceAdmin(admin.ModelAdmin):
    list_display = ['indicator_value', 'indicator_type', 'threat_type', 'confidence_level', 'source', 'last_seen']
    list_filter = ['indicator_type', 'threat_type', 'source', 'confidence_level', 'last_seen']
    search_fields = ['indicator_value', 'threat_type', 'source']
    ordering = ['-last_seen', '-confidence_level']

@admin.register(ScanReport)
class ScanReportAdmin(admin.ModelAdmin):
    list_display = ['scan', 'report_type', 'generated_date']
    list_filter = ['report_type', 'generated_date']
    search_fields = ['scan__url', 'scan__domain']
    readonly_fields = ['generated_date']
    ordering = ['-generated_date']

@admin.register(ScanConfiguration)
class ScanConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'enable_port_scan', 'enable_vulnerability_scan', 'created_date']
    list_filter = ['is_default', 'enable_port_scan', 'enable_vulnerability_scan', 'created_date']
    search_fields = ['name', 'description']
    readonly_fields = ['created_date']
    ordering = ['-is_default', 'name']

@admin.register(DataBreachCheck)
class DataBreachCheckAdmin(admin.ModelAdmin):
    list_display = ['email', 'breaches_found', 'check_date']
    list_filter = ['breaches_found', 'check_date']
    search_fields = ['email']
    readonly_fields = ['check_date']
    ordering = ['-check_date']
