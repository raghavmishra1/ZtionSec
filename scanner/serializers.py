"""
Django REST Framework Serializers for ZtionSec API
"""

from rest_framework import serializers
from .models import (
    SecurityScan, AdvancedSecurityScan, SecurityFinding, 
    DataBreachCheck, VulnerabilityDatabase, ThreatIntelligence
)

class SecurityScanSerializer(serializers.ModelSerializer):
    """Serializer for basic security scans"""
    
    class Meta:
        model = SecurityScan
        fields = [
            'id', 'url', 'scan_date', 'ssl_valid', 'ssl_issuer', 'ssl_expiry',
            'ssl_grade', 'has_hsts', 'has_csp', 'has_xframe', 'has_xss_protection',
            'has_content_type', 'cms_detected', 'cms_version', 'response_time',
            'status_code', 'security_score', 'grade', 'server_info', 'technologies',
            'vulnerabilities', 'risk_level'
        ]
        read_only_fields = ['id', 'scan_date']

class SecurityFindingSerializer(serializers.ModelSerializer):
    """Serializer for security findings"""
    
    class Meta:
        model = SecurityFinding
        fields = [
            'id', 'severity', 'category', 'title', 'description', 'recommendation',
            'cve_id', 'cvss_score', 'affected_component', 'proof_of_concept',
            'references', 'created_date'
        ]
        read_only_fields = ['id', 'created_date']

class AdvancedSecurityScanSerializer(serializers.ModelSerializer):
    """Serializer for advanced security scans"""
    findings = SecurityFindingSerializer(many=True, read_only=True)
    findings_count = serializers.SerializerMethodField()
    severity_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = AdvancedSecurityScan
        fields = [
            'id', 'url', 'domain', 'ip_address', 'scan_date', 'scan_duration',
            'security_score', 'risk_level', 'dns_analysis', 'ssl_analysis',
            'port_scan_results', 'webapp_scan_results', 'vulnerability_results',
            'subdomain_results', 'technology_stack', 'security_headers',
            'threat_intelligence', 'total_findings', 'critical_findings',
            'high_findings', 'medium_findings', 'low_findings', 'info_findings',
            'findings', 'findings_count', 'severity_breakdown'
        ]
        read_only_fields = ['id', 'scan_date']
    
    def get_findings_count(self, obj):
        """Get total number of findings"""
        return obj.findings.count()
    
    def get_severity_breakdown(self, obj):
        """Get breakdown of findings by severity"""
        findings = obj.findings.all()
        breakdown = {
            'critical': findings.filter(severity='critical').count(),
            'high': findings.filter(severity='high').count(),
            'medium': findings.filter(severity='medium').count(),
            'low': findings.filter(severity='low').count(),
            'info': findings.filter(severity='info').count(),
        }
        return breakdown

class DataBreachCheckSerializer(serializers.ModelSerializer):
    """Serializer for data breach checks"""
    
    class Meta:
        model = DataBreachCheck
        fields = [
            'id', 'email', 'check_date', 'breaches_found', 'breach_details'
        ]
        read_only_fields = ['id', 'check_date']

class VulnerabilityDatabaseSerializer(serializers.ModelSerializer):
    """Serializer for vulnerability database entries"""
    
    class Meta:
        model = VulnerabilityDatabase
        fields = [
            'cve_id', 'cvss_score', 'severity', 'description', 'published_date',
            'modified_date', 'affected_products', 'references', 'cached_date'
        ]
        read_only_fields = ['cached_date']

class ThreatIntelligenceSerializer(serializers.ModelSerializer):
    """Serializer for threat intelligence data"""
    
    class Meta:
        model = ThreatIntelligence
        fields = [
            'id', 'indicator_type', 'indicator_value', 'threat_type',
            'confidence_level', 'first_seen', 'last_seen', 'source',
            'additional_data'
        ]
        read_only_fields = ['id']

# Simplified serializers for API responses
class SimpleScanSerializer(serializers.ModelSerializer):
    """Simplified serializer for scan lists"""
    
    class Meta:
        model = AdvancedSecurityScan
        fields = [
            'id', 'url', 'domain', 'scan_date', 'security_score', 'risk_level',
            'total_findings', 'critical_findings', 'high_findings'
        ]

class ScanSummarySerializer(serializers.Serializer):
    """Serializer for scan summary statistics"""
    total_scans = serializers.IntegerField()
    total_findings = serializers.IntegerField()
    average_security_score = serializers.FloatField()
    risk_distribution = serializers.DictField()
    recent_scans = SimpleScanSerializer(many=True)
