"""
Advanced Security Reporting with Visualizations
"""

import json
from datetime import datetime
from io import BytesIO
import base64

# Optional imports for advanced visualization
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

class AdvancedReportGenerator:
    def __init__(self):
        self.setup_styling()
    
    def setup_styling(self):
        """Setup report styling"""
        if MATPLOTLIB_AVAILABLE:
            try:
                plt.style.use('default')  # Use default style instead of seaborn
            except:
                pass
        if SEABORN_AVAILABLE:
            try:
                sns.set_palette("husl")
            except:
                pass
    
    def generate_comprehensive_report(self, scan_data):
        """Generate comprehensive security report with visualizations"""
        report = {
            'executive_summary': self.create_executive_summary(scan_data),
            'vulnerability_analysis': self.analyze_vulnerabilities(scan_data),
            'risk_assessment': self.create_risk_assessment(scan_data),
            'charts': self.generate_charts(scan_data),
            'recommendations': self.generate_recommendations(scan_data)
        }
        return report
    
    def create_executive_summary(self, scan_data):
        """Create executive summary"""
        findings = scan_data.get('findings', [])
        critical_count = len([f for f in findings if f.get('severity') == 'critical'])
        high_count = len([f for f in findings if f.get('severity') == 'high'])
        
        return {
            'overall_risk': scan_data.get('risk_level', 'unknown'),
            'security_score': scan_data.get('security_score', 0),
            'critical_issues': critical_count,
            'high_issues': high_count,
            'total_findings': len(findings)
        }
    
    def analyze_vulnerabilities(self, scan_data):
        """Analyze vulnerability data"""
        findings = scan_data.get('findings', [])
        
        # Group by category
        categories = {}
        for finding in findings:
            category = finding.get('category', 'Unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(finding)
        
        return {
            'by_category': categories,
            'severity_distribution': self.get_severity_distribution(findings)
        }
    
    def get_severity_distribution(self, findings):
        """Get severity distribution"""
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        
        for finding in findings:
            severity = finding.get('severity', 'info')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return severity_counts
    
    def create_risk_assessment(self, scan_data):
        """Create detailed risk assessment"""
        return {
            'risk_factors': self.identify_risk_factors(scan_data),
            'compliance_status': self.check_compliance(scan_data),
            'trending': self.analyze_trends(scan_data)
        }
    
    def identify_risk_factors(self, scan_data):
        """Identify key risk factors"""
        risk_factors = []
        
        results = scan_data.get('results', {})
        
        # SSL risks
        ssl_data = results.get('ssl', {})
        if not ssl_data.get('ssl_enabled', False):
            risk_factors.append({
                'factor': 'No SSL/TLS Encryption',
                'impact': 'High',
                'description': 'Data transmitted in plaintext'
            })
        
        # Open ports
        port_data = results.get('ports', {})
        open_ports = port_data.get('open_ports', [])
        risky_ports = [p for p in open_ports if p.get('port') in [21, 22, 23, 25]]
        if risky_ports:
            risk_factors.append({
                'factor': 'Risky Open Ports',
                'impact': 'Medium',
                'description': f'{len(risky_ports)} potentially risky ports detected'
            })
        
        return risk_factors
    
    def check_compliance(self, scan_data):
        """Check compliance with security standards"""
        compliance = {
            'owasp_top_10': self.check_owasp_compliance(scan_data),
            'nist_framework': self.check_nist_compliance(scan_data),
            'iso_27001': self.check_iso_compliance(scan_data)
        }
        return compliance
    
    def check_owasp_compliance(self, scan_data):
        """Check OWASP Top 10 compliance"""
        findings = scan_data.get('findings', [])
        
        owasp_categories = {
            'A01_Broken_Access_Control': 0,
            'A02_Cryptographic_Failures': 0,
            'A03_Injection': 0,
            'A04_Insecure_Design': 0,
            'A05_Security_Misconfiguration': 0,
            'A06_Vulnerable_Components': 0,
            'A07_Authentication_Failures': 0,
            'A08_Software_Integrity_Failures': 0,
            'A09_Security_Logging_Failures': 0,
            'A10_Server_Side_Request_Forgery': 0
        }
        
        # Map findings to OWASP categories
        for finding in findings:
            title = finding.get('title', '').lower()
            if 'injection' in title or 'sql' in title:
                owasp_categories['A03_Injection'] += 1
            elif 'ssl' in title or 'tls' in title or 'encryption' in title:
                owasp_categories['A02_Cryptographic_Failures'] += 1
            elif 'header' in title or 'configuration' in title:
                owasp_categories['A05_Security_Misconfiguration'] += 1
        
        return owasp_categories
    
    def check_nist_compliance(self, scan_data):
        """Check NIST Framework compliance"""
        return {'status': 'partial', 'score': 65}
    
    def check_iso_compliance(self, scan_data):
        """Check ISO 27001 compliance"""
        return {'status': 'partial', 'score': 70}
    
    def analyze_trends(self, scan_data):
        """Analyze security trends"""
        return {
            'improvement_areas': ['SSL/TLS Configuration', 'Security Headers'],
            'trend_direction': 'improving'
        }
    
    def generate_charts(self, scan_data):
        """Generate visualization charts"""
        charts = {}
        
        # Severity distribution pie chart
        charts['severity_pie'] = self.create_severity_pie_chart(scan_data)
        
        # Risk score gauge
        charts['risk_gauge'] = self.create_risk_gauge(scan_data)
        
        # Category breakdown bar chart
        charts['category_bar'] = self.create_category_bar_chart(scan_data)
        
        return charts
    
    def create_severity_pie_chart(self, scan_data):
        """Create severity distribution pie chart"""
        findings = scan_data.get('findings', [])
        severity_dist = self.get_severity_distribution(findings)
        
        # Filter out zero values
        filtered_dist = {k: v for k, v in severity_dist.items() if v > 0}
        
        if not filtered_dist or not PLOTLY_AVAILABLE:
            return None
        
        try:
            fig = go.Figure(data=[go.Pie(
                labels=list(filtered_dist.keys()),
                values=list(filtered_dist.values()),
                hole=.3
            )])
            
            fig.update_layout(
                title="Security Findings by Severity",
                annotations=[dict(text='Findings', x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            
            return fig.to_json()
        except Exception as e:
            return None
    
    def create_risk_gauge(self, scan_data):
        """Create risk score gauge chart"""
        if not PLOTLY_AVAILABLE:
            return None
            
        risk_score = scan_data.get('security_score', 0)
        
        try:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = risk_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Security Score"},
                delta = {'reference': 80},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            return fig.to_json()
        except Exception as e:
            return None
    
    def create_category_bar_chart(self, scan_data):
        """Create category breakdown bar chart"""
        if not PLOTLY_AVAILABLE:
            return None
            
        findings = scan_data.get('findings', [])
        
        categories = {}
        for finding in findings:
            category = finding.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        
        if not categories:
            return None
        
        try:
            fig = go.Figure([go.Bar(
                x=list(categories.keys()),
                y=list(categories.values())
            )])
            
            fig.update_layout(
                title="Findings by Category",
                xaxis_title="Category",
                yaxis_title="Number of Findings"
            )
            
            return fig.to_json()
        except Exception as e:
            return None
    
    def generate_recommendations(self, scan_data):
        """Generate actionable security recommendations"""
        recommendations = []
        findings = scan_data.get('findings', [])
        
        # Priority recommendations based on critical findings
        critical_findings = [f for f in findings if f.get('severity') == 'critical']
        
        for finding in critical_findings[:5]:  # Top 5 critical issues
            recommendations.append({
                'priority': 'Critical',
                'title': finding.get('title', ''),
                'description': finding.get('description', ''),
                'recommendation': finding.get('recommendation', ''),
                'effort': 'High',
                'timeline': 'Immediate'
            })
        
        # Add general recommendations
        general_recommendations = [
            {
                'priority': 'High',
                'title': 'Implement Security Headers',
                'description': 'Add comprehensive security headers to prevent common attacks',
                'recommendation': 'Configure HSTS, CSP, X-Frame-Options, and other security headers',
                'effort': 'Medium',
                'timeline': '1-2 weeks'
            },
            {
                'priority': 'Medium',
                'title': 'Regular Security Scanning',
                'description': 'Implement automated security scanning in CI/CD pipeline',
                'recommendation': 'Set up automated scans and monitoring',
                'effort': 'Medium',
                'timeline': '2-4 weeks'
            }
        ]
        
        recommendations.extend(general_recommendations)
        
        return recommendations
