from django.db import models
from django.utils import timezone
import json

class SecurityScan(models.Model):
    url = models.URLField(max_length=500)
    scan_date = models.DateTimeField(default=timezone.now)
    
    # SSL Information
    ssl_valid = models.BooleanField(default=False)
    ssl_issuer = models.CharField(max_length=200, blank=True)
    ssl_expiry = models.DateTimeField(null=True, blank=True)
    ssl_grade = models.CharField(max_length=10, blank=True)
    
    # HTTP Security Headers
    has_hsts = models.BooleanField(default=False)
    has_csp = models.BooleanField(default=False)
    has_xframe = models.BooleanField(default=False)
    has_xss_protection = models.BooleanField(default=False)
    has_content_type = models.BooleanField(default=False)
    
    # CMS Detection
    cms_detected = models.CharField(max_length=100, blank=True)
    cms_version = models.CharField(max_length=50, blank=True)
    
    # Performance
    response_time = models.FloatField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    
    # Security Score
    security_score = models.IntegerField(default=0)
    grade = models.CharField(max_length=2, default='F')
    
    # Additional Info
    server_info = models.CharField(max_length=200, blank=True)
    technologies = models.TextField(blank=True)
    vulnerabilities = models.TextField(blank=True)
    
    # Advanced scan data
    advanced_scan_data = models.JSONField(default=dict, blank=True)
    risk_level = models.CharField(max_length=20, default='unknown')
    
    def __str__(self):
        return f"{self.url} - {self.grade} ({self.security_score}/100)"

class AdvancedSecurityScan(models.Model):
    """Enhanced security scan with comprehensive analysis"""
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    
    url = models.URLField(max_length=500)
    domain = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    scan_date = models.DateTimeField(default=timezone.now)
    scan_duration = models.FloatField(null=True, blank=True)  # in seconds
    
    # Overall Assessment
    security_score = models.IntegerField(default=0)  # 0-100
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='unknown')
    
    # Scan Results (JSON fields for flexibility)
    dns_analysis = models.JSONField(default=dict, blank=True)
    ssl_analysis = models.JSONField(default=dict, blank=True)
    port_scan_results = models.JSONField(default=dict, blank=True)
    webapp_scan_results = models.JSONField(default=dict, blank=True)
    vulnerability_results = models.JSONField(default=dict, blank=True)
    subdomain_results = models.JSONField(default=dict, blank=True)
    technology_stack = models.JSONField(default=dict, blank=True)
    security_headers = models.JSONField(default=dict, blank=True)
    threat_intelligence = models.JSONField(default=dict, blank=True)
    
    # Findings Summary
    total_findings = models.IntegerField(default=0)
    critical_findings = models.IntegerField(default=0)
    high_findings = models.IntegerField(default=0)
    medium_findings = models.IntegerField(default=0)
    low_findings = models.IntegerField(default=0)
    info_findings = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-scan_date']
    
    def __str__(self):
        return f"Advanced Scan: {self.url} - {self.risk_level} ({self.security_score}/100)"

class SecurityFinding(models.Model):
    """Individual security findings"""
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('info', 'Informational'),
    ]
    
    CATEGORY_CHOICES = [
        ('ssl_tls', 'SSL/TLS'),
        ('network', 'Network'),
        ('webapp', 'Web Application'),
        ('headers', 'Security Headers'),
        ('cms', 'CMS/Framework'),
        ('infrastructure', 'Infrastructure'),
        ('compliance', 'Compliance'),
        ('other', 'Other'),
    ]
    
    scan = models.ForeignKey(AdvancedSecurityScan, on_delete=models.CASCADE, related_name='findings')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    recommendation = models.TextField()
    
    # Optional CVE/vulnerability information
    cve_id = models.CharField(max_length=20, blank=True, null=True)
    cvss_score = models.FloatField(null=True, blank=True)
    
    # Additional metadata
    affected_component = models.CharField(max_length=200, blank=True)
    proof_of_concept = models.TextField(blank=True)
    references = models.JSONField(default=list, blank=True)
    
    created_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-cvss_score', '-created_date']
    
    def __str__(self):
        return f"{self.severity.upper()}: {self.title}"

class VulnerabilityDatabase(models.Model):
    """Local vulnerability database cache"""
    cve_id = models.CharField(max_length=20, unique=True, primary_key=True)
    cvss_score = models.FloatField()
    severity = models.CharField(max_length=20)
    description = models.TextField()
    published_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    affected_products = models.JSONField(default=list)
    references = models.JSONField(default=list)
    cached_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-cvss_score', '-published_date']
    
    def __str__(self):
        return f"{self.cve_id} - CVSS: {self.cvss_score}"

class ThreatIntelligence(models.Model):
    """Threat intelligence data"""
    INDICATOR_TYPES = [
        ('ip', 'IP Address'),
        ('domain', 'Domain'),
        ('url', 'URL'),
        ('hash', 'File Hash'),
    ]
    
    indicator_type = models.CharField(max_length=20, choices=INDICATOR_TYPES)
    indicator_value = models.CharField(max_length=500)
    threat_type = models.CharField(max_length=100, blank=True)
    confidence_level = models.IntegerField(default=0)  # 0-100
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField()
    source = models.CharField(max_length=100)
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        unique_together = ['indicator_type', 'indicator_value', 'source']
        ordering = ['-last_seen']
    
    def __str__(self):
        return f"{self.indicator_type.upper()}: {self.indicator_value}"

class ScanReport(models.Model):
    """Generated security reports"""
    REPORT_TYPES = [
        ('executive', 'Executive Summary'),
        ('technical', 'Technical Report'),
        ('compliance', 'Compliance Report'),
        ('comprehensive', 'Comprehensive Report'),
    ]
    
    scan = models.ForeignKey(AdvancedSecurityScan, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_date = models.DateTimeField(default=timezone.now)
    report_data = models.JSONField(default=dict)
    pdf_file = models.FileField(upload_to='reports/', blank=True, null=True)
    
    class Meta:
        ordering = ['-generated_date']
    
    def __str__(self):
        return f"{self.report_type.title()} Report - {self.scan.url}"

class DataBreachCheck(models.Model):
    email = models.EmailField()
    check_date = models.DateTimeField(default=timezone.now)
    breaches_found = models.IntegerField(default=0)
    breach_details = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.email} - {self.breaches_found} breaches"

class ScanConfiguration(models.Model):
    """Scan configuration profiles"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Scan options
    enable_port_scan = models.BooleanField(default=True)
    enable_vulnerability_scan = models.BooleanField(default=True)
    enable_webapp_scan = models.BooleanField(default=True)
    enable_subdomain_enum = models.BooleanField(default=True)
    enable_threat_intel = models.BooleanField(default=True)
    
    # Scan parameters
    port_scan_range = models.CharField(max_length=100, default='1-1000')
    scan_timeout = models.IntegerField(default=300)  # seconds
    max_threads = models.IntegerField(default=10)
    
    # Additional configuration
    custom_wordlists = models.JSONField(default=list, blank=True)
    excluded_checks = models.JSONField(default=list, blank=True)
    
    created_date = models.DateTimeField(default=timezone.now)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
