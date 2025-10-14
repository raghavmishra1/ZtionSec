try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from io import BytesIO
from datetime import datetime

def generate_security_report(scan):
    """Generate a comprehensive PDF security report"""
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab is not installed. Please install it with: pip install reportlab")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Title
    title = Paragraph("ZtionSec Security Analysis Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Basic Information
    basic_info = [
        ['Website URL:', scan.url],
        ['Scan Date:', scan.scan_date.strftime('%Y-%m-%d %H:%M:%S')],
        ['Security Grade:', scan.grade],
        ['Security Score:', f"{scan.security_score}/100"],
    ]
    
    basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(basic_table)
    elements.append(Spacer(1, 20))
    
    # SSL Certificate Section
    ssl_heading = Paragraph("SSL Certificate Analysis", heading_style)
    elements.append(ssl_heading)
    
    ssl_status = "Valid" if scan.ssl_valid else "Invalid"
    ssl_color = colors.green if scan.ssl_valid else colors.red
    
    ssl_info = [
        ['SSL Status:', ssl_status],
        ['SSL Grade:', scan.ssl_grade],
        ['Issuer:', scan.ssl_issuer or 'N/A'],
        ['Expiry Date:', scan.ssl_expiry.strftime('%Y-%m-%d') if scan.ssl_expiry else 'N/A'],
    ]
    
    ssl_table = Table(ssl_info, colWidths=[2*inch, 4*inch])
    ssl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (1, 0), (1, 0), ssl_color),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(ssl_table)
    elements.append(Spacer(1, 20))
    
    # Security Headers Section
    headers_heading = Paragraph("HTTP Security Headers", heading_style)
    elements.append(headers_heading)
    
    def get_status_color(status):
        return colors.green if status else colors.red
    
    def get_status_text(status):
        return "Present" if status else "Missing"
    
    headers_info = [
        ['Header', 'Status'],
        ['HSTS (Strict-Transport-Security)', get_status_text(scan.has_hsts)],
        ['CSP (Content-Security-Policy)', get_status_text(scan.has_csp)],
        ['X-Frame-Options', get_status_text(scan.has_xframe)],
        ['X-XSS-Protection', get_status_text(scan.has_xss_protection)],
        ['X-Content-Type-Options', get_status_text(scan.has_content_type)],
    ]
    
    headers_table = Table(headers_info, colWidths=[3*inch, 2*inch])
    headers_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (1, 1), (1, 1), get_status_color(scan.has_hsts)),
        ('TEXTCOLOR', (1, 2), (1, 2), get_status_color(scan.has_csp)),
        ('TEXTCOLOR', (1, 3), (1, 3), get_status_color(scan.has_xframe)),
        ('TEXTCOLOR', (1, 4), (1, 4), get_status_color(scan.has_xss_protection)),
        ('TEXTCOLOR', (1, 5), (1, 5), get_status_color(scan.has_content_type)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(headers_table)
    elements.append(Spacer(1, 20))
    
    # Performance Section
    performance_heading = Paragraph("Performance Analysis", heading_style)
    elements.append(performance_heading)
    
    performance_info = [
        ['Response Time:', f"{scan.response_time}ms" if scan.response_time else 'N/A'],
        ['HTTP Status Code:', str(scan.status_code) if scan.status_code else 'N/A'],
        ['Server Information:', scan.server_info or 'N/A'],
    ]
    
    performance_table = Table(performance_info, colWidths=[2*inch, 4*inch])
    performance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(performance_table)
    elements.append(Spacer(1, 20))
    
    # CMS Detection Section
    cms_heading = Paragraph("Technology Detection", heading_style)
    elements.append(cms_heading)
    
    # Use generic terms for client reports to hide internal technology details
    cms_display = scan.cms_detected or 'Unknown'
    if cms_display == 'Django':
        cms_display = 'Web Application Framework'
    elif cms_display == 'Laravel':
        cms_display = 'PHP Framework'
    elif cms_display == 'Flask':
        cms_display = 'Python Web Framework'
    
    cms_info = [
        ['Platform Detected:', cms_display],
        ['Version:', scan.cms_version or 'N/A'],
    ]
    
    cms_table = Table(cms_info, colWidths=[2*inch, 4*inch])
    cms_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(cms_table)
    elements.append(Spacer(1, 20))
    
    # Recommendations Section
    recommendations_heading = Paragraph("Security Recommendations", heading_style)
    elements.append(recommendations_heading)
    
    recommendations = []
    
    if not scan.ssl_valid:
        recommendations.append("• Implement SSL/TLS certificate for secure communication")
    
    if not scan.has_hsts:
        recommendations.append("• Add HTTP Strict Transport Security (HSTS) header")
    
    if not scan.has_csp:
        recommendations.append("• Implement Content Security Policy (CSP) header")
    
    if not scan.has_xframe:
        recommendations.append("• Add X-Frame-Options header to prevent clickjacking")
    
    if not scan.has_xss_protection:
        recommendations.append("• Enable X-XSS-Protection header")
    
    if not scan.has_content_type:
        recommendations.append("• Add X-Content-Type-Options header")
    
    if scan.response_time and scan.response_time > 3000:
        recommendations.append("• Optimize website performance to reduce response time")
    
    if not recommendations:
        recommendations.append("• Great job! Your website follows security best practices.")
    
    for rec in recommendations:
        elements.append(Paragraph(rec, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(Spacer(1, 20))
    
    # Footer
    footer_text = f"Report generated by ZtionSec on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    footer = Paragraph(footer_text, styles['Normal'])
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and return it
    buffer.seek(0)
    return buffer
