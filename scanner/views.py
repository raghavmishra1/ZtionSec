from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.paginator import Paginator
import json
import time
from datetime import datetime
import logging

from .models import SecurityScan, DataBreachCheck
from .utils import SecurityScanner
try:
    from .utils import HaveIBeenPwnedChecker
except ImportError:
    HaveIBeenPwnedChecker = None
from .pdf_generator import generate_security_report
import json

# Security logger
security_logger = logging.getLogger('security')

def home(request):
    """Home page with scanning interface"""
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Avg
    
    # Get real data from database
    recent_scans = SecurityScan.objects.order_by('-scan_date')[:5]
    
    # Calculate real statistics
    today = timezone.now().date()
    scans_today = SecurityScan.objects.filter(scan_date__date=today).count()
    total_scans = SecurityScan.objects.count()
    
    # Calculate average security score
    avg_score = SecurityScan.objects.aggregate(avg_score=Avg('security_score'))['avg_score']
    avg_security_score = f"{int(avg_score)}%" if avg_score else "87%"
    
    # Count vulnerabilities (simulated based on low scores)
    total_vulnerabilities = SecurityScan.objects.filter(security_score__lt=70).count()
    
    # SSL issues (simulated based on SSL grade)
    ssl_issues = SecurityScan.objects.exclude(ssl_grade__in=['A+', 'A', 'A-']).count()
    
    # Threats blocked (simulated)
    threats_blocked = total_vulnerabilities * 3  # Approximate multiplier
    
    # Breach databases count
    breach_databases = 15  # Number of databases we check
    
    context = {
        'recent_scans': recent_scans,
        'total_scans': total_scans,
        'scans_today': scans_today,
        'total_vulnerabilities': total_vulnerabilities,
        'threats_blocked': f"{threats_blocked:,}",
        'ssl_issues': ssl_issues,
        'avg_security_score': avg_security_score,
        'breach_databases': breach_databases,
    }
    
    return render(request, 'scanner/home.html', context)

def scan_website(request):
    """Perform website security scan"""
    if request.method == 'POST':
        url = request.POST.get('url')
        print(f"DEBUG: Received URL: {url}")  # Debug logging
        
        if not url:
            messages.error(request, 'Please provide a valid URL')
            return redirect('home')
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            print(f"DEBUG: Starting scan for URL: {url}")  # Debug logging
            
            # Perform security scan
            scanner = SecurityScanner(url)
            results = scanner.scan_all()
            
            print(f"DEBUG: Scan results: {results}")  # Debug logging
            
            # Save to database
            scan = SecurityScan.objects.create(
                url=url,
                ssl_valid=results.get('ssl_valid', False),
                ssl_issuer=results.get('ssl_issuer', ''),
                ssl_expiry=results.get('ssl_expiry'),
                ssl_grade=results.get('ssl_grade', 'F'),
                has_hsts=results.get('has_hsts', False),
                has_csp=results.get('has_csp', False),
                has_xframe=results.get('has_xframe', False),
                has_xss_protection=results.get('has_xss_protection', False),
                has_content_type=results.get('has_content_type', False),
                cms_detected=results.get('cms_detected', ''),
                cms_version=results.get('cms_version', ''),
                response_time=results.get('response_time'),
                status_code=results.get('status_code'),
                security_score=results.get('security_score', 0),
                grade=results.get('grade', 'F'),
                server_info=results.get('server_info', ''),
            )
            
            print(f"DEBUG: Scan saved with ID: {scan.id}")  # Debug logging
            
            return render(request, 'scanner/results.html', {
                'scan': scan,
                'results': results
            })
            
        except Exception as e:
            messages.error(request, f'Error scanning website: {str(e)}')
            return redirect('home')
    
    return redirect('home')

@csrf_exempt
def api_scan(request):
    """API endpoint for website scanning"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')
            
            if not url:
                return JsonResponse({'error': 'URL is required'}, status=400)
            
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            scanner = SecurityScanner(url)
            results = scanner.scan_all()
            
            return JsonResponse(results)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

def check_breach(request):
    """Check email for data breaches"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Please provide a valid email address')
            return redirect('home')
        
        try:
            if HaveIBeenPwnedChecker is None:
                messages.error(request, 'Breach checking service is currently unavailable')
                return redirect('home')
            
            checker = HaveIBeenPwnedChecker()
            results = checker.check_email(email)
            
            # Save to database
            breach_check = DataBreachCheck.objects.create(
                email=email,
                breaches_found=results.get('breaches_found', 0),
                breach_details=json.dumps(results.get('breach_details', []))
            )
            
            return render(request, 'scanner/breach_results.html', {
                'breach_check': breach_check,
                'results': results
            })
            
        except Exception as e:
            messages.error(request, f'Error checking email: {str(e)}')
            return redirect('home')
    
    return redirect('home')

def generate_report(request, scan_id):
    """Generate PDF report for a scan"""
    try:
        scan = SecurityScan.objects.get(id=scan_id)
        pdf_buffer = generate_security_report(scan)
        
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="security_report_{scan.id}.pdf"'
        
        return response
        
    except SecurityScan.DoesNotExist:
        messages.error(request, 'Scan not found')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('home')

def scan_history(request):
    """View scan history"""
    scans = SecurityScan.objects.order_by('-scan_date')
    return render(request, 'scanner/history.html', {
        'scans': scans
    })

def breach_history(request):
    """View breach check history"""
    checks = DataBreachCheck.objects.order_by('-check_date')
    return render(request, 'scanner/breach_history.html', {
        'checks': checks
    })

def about(request):
    """About page"""
    return render(request, 'scanner/about.html')

def contact(request):
    """Contact page"""
    return render(request, 'scanner/contact.html')

def budget_scanner(request):
    """Budget scanner page for P4 vulnerabilities"""
    # Get some sample recent scans for display
    recent_scans = []  # Placeholder for now
    return render(request, 'scanner/budget_scanner.html', {
        'recent_scans': recent_scans
    })

def budget_scan(request):
    """Perform budget security scan"""
    if request.method == 'GET':
        # If someone accesses /budget-scan/ directly, redirect to budget scanner
        return redirect('budget_scanner')
    
    if request.method == 'POST':
        target_url = request.POST.get('target_url')
        scan_types = request.POST.getlist('scan_types') or ['basic']
        
        print(f"Budget scan request: URL={target_url}, Types={scan_types}")  # Debug
        
        if not target_url:
            messages.error(request, 'Please provide a valid URL')
            return redirect('budget_scanner')
        
        # Ensure URL has protocol
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
        
        try:
            print(f"Starting budget scan for: {target_url}")  # Debug
            
            # Simple budget scan using basic security scanner
            scanner = SecurityScanner(target_url)
            results = scanner.scan_all()
            
            print(f"Scanner results: {results}")  # Debug
            
            # Create budget-style findings from regular scan results
            findings = []
            
            # Check for common P4 issues
            if not results.get('has_hsts', False):
                findings.append({
                    'severity': 'low',
                    'category': 'security_headers',
                    'title': 'Missing HSTS Header',
                    'description': 'The website does not implement HTTP Strict Transport Security',
                    'recommendation': 'Add HSTS header to prevent protocol downgrade attacks',
                    'bounty_potential': '$50-$200'
                })
            
            if not results.get('has_csp', False):
                findings.append({
                    'severity': 'low',
                    'category': 'security_headers',
                    'title': 'Missing Content Security Policy',
                    'description': 'No CSP header found, potential XSS vulnerability',
                    'recommendation': 'Implement a strict Content Security Policy',
                    'bounty_potential': '$100-$500'
                })
            
            if not results.get('has_xframe', False):
                findings.append({
                    'severity': 'low',
                    'category': 'security_headers',
                    'title': 'Missing X-Frame-Options',
                    'description': 'Website may be vulnerable to clickjacking attacks',
                    'recommendation': 'Add X-Frame-Options: DENY or SAMEORIGIN header',
                    'bounty_potential': '$50-$300'
                })
            
            print(f"Generated {len(findings)} findings")  # Debug
            
            # Store results in session for display
            request.session['budget_scan_results'] = {
                'target_url': target_url,
                'findings': findings,
                'scan_time': datetime.now().isoformat(),
                'total_findings': len(findings),
                'scan_types': scan_types
            }
            
            print("Results stored in session, redirecting to budget_results")  # Debug
            
            messages.success(request, f'Budget scan completed! Found {len(findings)} potential P4 vulnerabilities.')
            return redirect('budget_results')
            
        except Exception as e:
            error_msg = f'Error during budget scan: {str(e)}'
            messages.error(request, error_msg)
            print(f"Budget scan error: {e}")
            import traceback
            traceback.print_exc()  # Full error trace
            return redirect('budget_scanner')
    
    return redirect('budget_scanner')

def budget_results(request):
    """Display budget scan results"""
    results = request.session.get('budget_scan_results')
    
    if not results:
        messages.error(request, 'No scan results found. Please run a scan first.')
        return redirect('budget_scanner')
    
    return render(request, 'scanner/budget_results.html', {
        'results': results
    })

# Custom Error Handlers to Prevent Information Disclosure
def custom_404(request, exception):
    """Custom 404 handler that doesn't reveal system information"""
    # Log the 404 attempt for security monitoring
    security_logger.warning(
        f"404 Error: {request.method} {request.path} "
        f"from {request.META.get('REMOTE_ADDR', 'unknown')} "
        f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'unknown')}"
    )
    
    # Return generic 404 page without revealing system details
    return render(request, '404.html', status=404)

def custom_500(request):
    """Custom 500 handler that doesn't reveal system information"""
    # Log the 500 error for security monitoring
    security_logger.error(
        f"500 Error: {request.method} {request.path} "
        f"from {request.META.get('REMOTE_ADDR', 'unknown')} "
        f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'unknown')}"
    )
    
    # Return generic 500 page without revealing system details
    return render(request, '500.html', status=500)

def security_info(request):
    """Security information endpoint for administrators only"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        security_logger.warning(
            f"Unauthorized access to security info: {request.method} {request.path} "
            f"from {request.META.get('REMOTE_ADDR', 'unknown')}"
        )
        raise Http404("Page not found")
    
    # Provide security information only to superusers
    security_info = {
        'server_info': 'ZtionSec Security Platform v1.0',
        'security_headers': 'Enabled',
        'ssl_status': 'Active',
        'admin_panel': 'Secured',
        'last_security_scan': datetime.now().isoformat()
    }
    
    return JsonResponse(security_info)

def modal_test(request):
    """Modal system test page"""
    return render(request, 'scanner/modal_test.html')

# Resource Pages
def documentation(request):
    """Documentation page"""
    return render(request, 'scanner/documentation.html')

def tutorials(request):
    """Tutorials page"""
    return render(request, 'scanner/tutorials.html')

def faq(request):
    """FAQ page"""
    return render(request, 'scanner/faq.html')

# Enterprise Pages
def enterprise(request):
    """Enterprise solutions page"""
    return render(request, 'scanner/enterprise.html')

def api_access(request):
    """API access page"""
    return render(request, 'scanner/api_access.html')

def team_plans(request):
    """Team plans page"""
    return render(request, 'scanner/team_plans.html')

def partnerships(request):
    """Partnerships page"""
    return render(request, 'scanner/partnerships.html')

# Scanner Pages
def breach_check_page(request):
    """Breach check page"""
    return render(request, 'scanner/breach_check.html')

def cve_database(request):
    """CVE database page"""
    from .models import VulnerabilityDatabase
    
    # Get recent CVEs
    recent_cves = VulnerabilityDatabase.objects.all()[:20]
    
    context = {
        'recent_cves': recent_cves,
        'total_cves': VulnerabilityDatabase.objects.count(),
    }
    return render(request, 'scanner/cve_database.html', context)

# Newsletter
def newsletter_signup(request):
    """Newsletter signup page"""
    return render(request, 'scanner/newsletter.html')

def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # Here you would typically save to database or send to email service
            messages.success(request, 'Successfully subscribed to security updates!')
        else:
            messages.error(request, 'Please provide a valid email address.')
    
    return redirect('newsletter_signup')

def quick_scan(request):
    """Quick scan page with simplified interface"""
    return render(request, 'scanner/quick_scan.html')

def security_analytics(request):
    """Security analytics page"""
    return render(request, 'scanner/security_analytics.html')

def advanced_dashboard(request):
    """Advanced dashboard page"""
    return render(request, 'scanner/advanced_dashboard.html')

# Health Check Endpoints for Production
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
import json

@cache_page(60)  # Cache for 1 minute
@require_http_methods(["GET"])
def health_check(request):
    """Lightweight health check for Render"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'ztionsec',
        'version': '1.0.0'
    }, status=200)

@cache_page(60)  # Cache for 1 minute  
@require_http_methods(["GET"])
def api_health_check(request):
    """API health check endpoint"""
    return JsonResponse({
        'status': 'ok',
        'timestamp': '2025-10-15T00:00:00Z',
        'service': 'ztionsec-api'
    }, status=200)
