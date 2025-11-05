"""
Integrated Security System for ZtionSec
Combines all security components for comprehensive protection
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import json

from .enhanced_vulnerability_validator import VulnerabilityValidator, ValidatedVulnerability
from .permission_verification import PermissionVerificationSystem, ScanningEthicsEnforcer
from .legal_compliance import LegalComplianceSystem, DataRetentionManager
from .modern_vulnerability_detector import ModernVulnerabilityDetector, ModernVulnerability

logger = logging.getLogger(__name__)

@dataclass
class ScanRequest:
    """Comprehensive scan request with all metadata"""
    target_url: str
    scan_type: str  # basic, advanced, budget, comprehensive
    user_identifier: str
    user_info: Dict[str, Any]
    scan_config: Dict[str, Any]
    request_metadata: Dict[str, Any]

@dataclass
class ScanResult:
    """Comprehensive scan result with validation and compliance"""
    scan_id: str
    target_url: str
    scan_type: str
    permission_granted: bool
    compliance_status: str
    vulnerabilities: List[ValidatedVulnerability]
    validation_report: Dict[str, Any]
    legal_compliance: Dict[str, Any]
    scan_metadata: Dict[str, Any]
    recommendations: List[str]
    
class IntegratedSecuritySystem:
    """Main security system integrating all components"""
    
    def __init__(self):
        self.vulnerability_validator = VulnerabilityValidator()
        self.permission_system = PermissionVerificationSystem()
        self.ethics_enforcer = ScanningEthicsEnforcer(self.permission_system)
        self.legal_compliance = LegalComplianceSystem()
        self.data_retention = DataRetentionManager()
        
    def process_scan_request(self, scan_request: ScanRequest) -> Tuple[bool, ScanResult]:
        """
        Process a comprehensive scan request with full security validation
        
        Returns:
            (success, scan_result)
        """
        
        scan_id = self._generate_scan_id(scan_request)
        
        try:
            # Step 1: Legal Compliance Check
            compliance_valid, compliance_violations = self.legal_compliance.enforce_terms_compliance(
                scan_request.user_identifier,
                f"scan_{scan_request.scan_type}",
                {
                    'target_url': scan_request.target_url,
                    'ip_address': scan_request.request_metadata.get('ip_address'),
                    'user_agent': scan_request.request_metadata.get('user_agent')
                }
            )
            
            if not compliance_valid:
                return False, ScanResult(
                    scan_id=scan_id,
                    target_url=scan_request.target_url,
                    scan_type=scan_request.scan_type,
                    permission_granted=False,
                    compliance_status='failed',
                    vulnerabilities=[],
                    validation_report={},
                    legal_compliance={'violations': compliance_violations},
                    scan_metadata={'error': 'Legal compliance check failed'},
                    recommendations=['Address compliance violations before scanning']
                )
            
            # Step 2: Permission Verification
            authorized, auth_reason, verification_token = self.ethics_enforcer.authorize_scan(
                scan_request.target_url,
                scan_request.scan_config,
                scan_request.user_info
            )
            
            if not authorized:
                return False, ScanResult(
                    scan_id=scan_id,
                    target_url=scan_request.target_url,
                    scan_type=scan_request.scan_type,
                    permission_granted=False,
                    compliance_status='permission_denied',
                    vulnerabilities=[],
                    validation_report={},
                    legal_compliance={'status': 'compliant'},
                    scan_metadata={'error': auth_reason},
                    recommendations=['Obtain proper scanning permission']
                )
            
            # Step 3: Perform Vulnerability Scan
            raw_vulnerabilities = self._perform_vulnerability_scan(
                scan_request.target_url,
                scan_request.scan_type,
                verification_token
            )
            
            # Step 4: Validate Vulnerabilities
            validated_vulnerabilities = []
            for vuln in raw_vulnerabilities:
                validated_vuln = self.vulnerability_validator.validate_vulnerability(vuln)
                validated_vulnerabilities.append(validated_vuln)
            
            # Step 5: Filter High-Confidence Vulnerabilities
            high_confidence_vulns = self.vulnerability_validator.filter_high_confidence_vulnerabilities(
                raw_vulnerabilities,
                min_confidence=0.6
            )
            
            # Step 6: Generate Validation Report
            validation_report = self.vulnerability_validator.generate_validation_report(
                validated_vulnerabilities
            )
            
            # Step 7: Generate Recommendations
            recommendations = self._generate_comprehensive_recommendations(
                validated_vulnerabilities,
                validation_report,
                scan_request.scan_type
            )
            
            # Step 8: Log Scan for Audit
            self._log_scan_activity(scan_request, validated_vulnerabilities, verification_token)
            
            return True, ScanResult(
                scan_id=scan_id,
                target_url=scan_request.target_url,
                scan_type=scan_request.scan_type,
                permission_granted=True,
                compliance_status='compliant',
                vulnerabilities=validated_vulnerabilities,
                validation_report=validation_report,
                legal_compliance={'status': 'compliant', 'token': verification_token},
                scan_metadata={
                    'scan_duration': 0,  # Would be calculated
                    'total_checks': len(raw_vulnerabilities),
                    'validation_method': 'enhanced_validation'
                },
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error processing scan request: {str(e)}")
            return False, ScanResult(
                scan_id=scan_id,
                target_url=scan_request.target_url,
                scan_type=scan_request.scan_type,
                permission_granted=False,
                compliance_status='error',
                vulnerabilities=[],
                validation_report={},
                legal_compliance={'status': 'error'},
                scan_metadata={'error': str(e)},
                recommendations=['Contact support for assistance']
            )
    
    def _perform_vulnerability_scan(self, target_url: str, scan_type: str, 
                                  verification_token: str) -> List[Dict[str, Any]]:
        """Perform the actual vulnerability scan"""
        
        vulnerabilities = []
        
        try:
            if scan_type in ['comprehensive', 'advanced']:
                # Use modern vulnerability detector
                detector = ModernVulnerabilityDetector(target_url)
                modern_vulns = detector.comprehensive_vulnerability_scan()
                
                # Convert to dictionary format
                for vuln in modern_vulns:
                    vulnerabilities.append({
                        'cve_id': vuln.cve_id,
                        'severity': vuln.severity,
                        'category': vuln.owasp_category,
                        'title': vuln.title,
                        'description': vuln.description,
                        'recommendation': vuln.remediation,
                        'confidence_score': vuln.confidence,
                        'detection_method': vuln.detection_method,
                        'proof_of_concept': vuln.proof_of_concept,
                        'references': vuln.references,
                        'attack_vector': vuln.attack_vector,
                        'exploit_complexity': vuln.exploit_complexity
                    })
            
            elif scan_type == 'budget':
                # Use budget scanner for P4 vulnerabilities
                from .budget_scanner import BudgetSecurityScanner
                
                budget_scanner = BudgetSecurityScanner(target_url)
                budget_findings = budget_scanner.scan_all_budget_issues()
                
                # Convert to dictionary format
                for finding in budget_findings:
                    vulnerabilities.append({
                        'cve_id': None,
                        'severity': finding.severity,
                        'category': finding.category,
                        'title': finding.title,
                        'description': finding.description,
                        'recommendation': finding.recommendation,
                        'confidence_score': 0.7,  # Default for budget scans
                        'detection_method': 'pattern_matching',
                        'proof_of_concept': finding.proof_of_concept,
                        'references': [],
                        'attack_vector': 'network',
                        'exploit_complexity': finding.difficulty
                    })
            
            else:  # basic scan
                # Use basic security scanner
                from .utils import SecurityScanner
                
                scanner = SecurityScanner(target_url)
                basic_results = scanner.scan_all()
                
                # Convert basic results to vulnerability format
                if basic_results.get('security_score', 100) < 70:
                    vulnerabilities.append({
                        'cve_id': None,
                        'severity': 'medium',
                        'category': 'security_misconfiguration',
                        'title': 'Low Security Score',
                        'description': f'Overall security score: {basic_results.get("security_score", 0)}%',
                        'recommendation': 'Review and improve security configuration',
                        'confidence_score': 0.8,
                        'detection_method': 'security_assessment',
                        'proof_of_concept': f'Security score: {basic_results.get("security_score", 0)}%',
                        'references': [],
                        'attack_vector': 'network',
                        'exploit_complexity': 'low'
                    })
        
        except Exception as e:
            logger.error(f"Error performing vulnerability scan: {str(e)}")
            # Return a scan error as a finding
            vulnerabilities.append({
                'cve_id': None,
                'severity': 'info',
                'category': 'scan_error',
                'title': 'Scan Error',
                'description': f'Error during vulnerability scan: {str(e)}',
                'recommendation': 'Retry scan or contact support',
                'confidence_score': 1.0,
                'detection_method': 'error_detection',
                'proof_of_concept': str(e),
                'references': [],
                'attack_vector': 'unknown',
                'exploit_complexity': 'unknown'
            })
        
        return vulnerabilities
    
    def _generate_comprehensive_recommendations(self, vulnerabilities: List[ValidatedVulnerability],
                                             validation_report: Dict[str, Any],
                                             scan_type: str) -> List[str]:
        """Generate comprehensive security recommendations"""
        
        recommendations = []
        
        # Priority-based recommendations
        critical_vulns = [v for v in vulnerabilities if v.severity == 'critical']
        high_vulns = [v for v in vulnerabilities if v.severity == 'high']
        
        if critical_vulns:
            recommendations.append(f"🚨 URGENT: Address {len(critical_vulns)} critical vulnerabilities immediately")
        
        if high_vulns:
            recommendations.append(f"⚠️ HIGH PRIORITY: Fix {len(high_vulns)} high-severity vulnerabilities")
        
        # Confidence-based recommendations
        low_confidence_vulns = [v for v in vulnerabilities if v.confidence_score < 0.6]
        if low_confidence_vulns:
            recommendations.append(f"🔍 VERIFY: Manually verify {len(low_confidence_vulns)} low-confidence findings")
        
        # Category-specific recommendations
        categories = {}
        for vuln in vulnerabilities:
            category = vuln.category
            categories[category] = categories.get(category, 0) + 1
        
        for category, count in categories.items():
            if count > 2:
                recommendations.append(f"📋 FOCUS AREA: {category.replace('_', ' ').title()} - {count} issues found")
        
        # Scan type specific recommendations
        if scan_type == 'budget':
            recommendations.append("💰 BUDGET TIP: Focus on easy-to-fix P4 vulnerabilities for quick wins")
        elif scan_type == 'comprehensive':
            recommendations.append("🔬 COMPREHENSIVE: Consider implementing a regular scanning schedule")
        
        # General security recommendations
        if len(vulnerabilities) == 0:
            recommendations.append("✅ EXCELLENT: No vulnerabilities detected - maintain current security posture")
        else:
            recommendations.append("🛡️ SECURITY: Implement a vulnerability management program")
            recommendations.append("📚 TRAINING: Provide security awareness training to development team")
        
        return recommendations
    
    def _generate_scan_id(self, scan_request: ScanRequest) -> str:
        """Generate unique scan ID"""
        import hashlib
        import time
        
        data = f"{scan_request.target_url}_{scan_request.user_identifier}_{time.time()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _log_scan_activity(self, scan_request: ScanRequest, 
                          vulnerabilities: List[ValidatedVulnerability],
                          verification_token: str):
        """Log scan activity for audit trail"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'target_url': scan_request.target_url,
            'scan_type': scan_request.scan_type,
            'user_identifier': scan_request.user_identifier,
            'verification_token': verification_token,
            'vulnerabilities_found': len(vulnerabilities),
            'high_severity_count': len([v for v in vulnerabilities if v.severity in ['critical', 'high']]),
            'compliance_status': 'compliant'
        }
        
        logger.info(f"Scan activity: {json.dumps(log_entry)}")
    
    def generate_security_report(self, scan_result: ScanResult) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        
        report = {
            'executive_summary': {
                'scan_id': scan_result.scan_id,
                'target_url': scan_result.target_url,
                'scan_date': datetime.now().isoformat(),
                'total_vulnerabilities': len(scan_result.vulnerabilities),
                'risk_level': self._calculate_risk_level(scan_result.vulnerabilities),
                'compliance_status': scan_result.compliance_status
            },
            'vulnerability_summary': {
                'by_severity': self._count_by_severity(scan_result.vulnerabilities),
                'by_category': self._count_by_category(scan_result.vulnerabilities),
                'confidence_distribution': self._analyze_confidence_distribution(scan_result.vulnerabilities)
            },
            'detailed_findings': [
                {
                    'title': vuln.title,
                    'severity': vuln.severity,
                    'confidence': vuln.confidence_score,
                    'category': vuln.category,
                    'description': vuln.description,
                    'recommendation': vuln.recommendation,
                    'validation_method': vuln.validation_method,
                    'false_positive_likelihood': vuln.false_positive_likelihood
                }
                for vuln in scan_result.vulnerabilities
            ],
            'validation_report': scan_result.validation_report,
            'recommendations': scan_result.recommendations,
            'compliance_information': {
                'legal_compliance': scan_result.legal_compliance,
                'permission_status': scan_result.permission_granted,
                'data_retention_policy': 'Applied according to policy'
            },
            'next_steps': self._generate_next_steps(scan_result)
        }
        
        return report
    
    def _calculate_risk_level(self, vulnerabilities: List[ValidatedVulnerability]) -> str:
        """Calculate overall risk level"""
        if not vulnerabilities:
            return 'low'
        
        critical_count = len([v for v in vulnerabilities if v.severity == 'critical'])
        high_count = len([v for v in vulnerabilities if v.severity == 'high'])
        
        if critical_count > 0:
            return 'critical'
        elif high_count > 2:
            return 'high'
        elif high_count > 0:
            return 'medium'
        else:
            return 'low'
    
    def _count_by_severity(self, vulnerabilities: List[ValidatedVulnerability]) -> Dict[str, int]:
        """Count vulnerabilities by severity"""
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        
        for vuln in vulnerabilities:
            if vuln.severity in counts:
                counts[vuln.severity] += 1
        
        return counts
    
    def _count_by_category(self, vulnerabilities: List[ValidatedVulnerability]) -> Dict[str, int]:
        """Count vulnerabilities by category"""
        counts = {}
        
        for vuln in vulnerabilities:
            category = vuln.category
            counts[category] = counts.get(category, 0) + 1
        
        return counts
    
    def _analyze_confidence_distribution(self, vulnerabilities: List[ValidatedVulnerability]) -> Dict[str, int]:
        """Analyze confidence score distribution"""
        distribution = {'high': 0, 'medium': 0, 'low': 0}
        
        for vuln in vulnerabilities:
            if vuln.confidence_score >= 0.8:
                distribution['high'] += 1
            elif vuln.confidence_score >= 0.6:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        
        return distribution
    
    def _generate_next_steps(self, scan_result: ScanResult) -> List[str]:
        """Generate next steps based on scan results"""
        next_steps = []
        
        if not scan_result.vulnerabilities:
            next_steps.append("Continue monitoring with regular security scans")
            next_steps.append("Implement proactive security measures")
        else:
            next_steps.append("Prioritize fixing critical and high-severity vulnerabilities")
            next_steps.append("Verify low-confidence findings manually")
            next_steps.append("Implement security controls to prevent similar issues")
            next_steps.append("Schedule follow-up scan after remediation")
        
        next_steps.append("Review and update security policies")
        next_steps.append("Consider implementing continuous security monitoring")
        
        return next_steps
    
    def cleanup_old_data(self):
        """Clean up old data according to retention policies"""
        
        # Apply data retention policies
        cleanup_results = {}
        
        data_types = ['scan_results', 'user_data', 'logs', 'consent_records', 'violation_logs']
        
        for data_type in data_types:
            result = self.data_retention.apply_retention_policy(data_type)
            cleanup_results[data_type] = result
        
        logger.info(f"Data cleanup completed: {json.dumps(cleanup_results)}")
        
        return cleanup_results
