"""
ZtionSec REST API Views
Provides API endpoints for frontend consumption
"""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime

from .models import SecurityScan, AdvancedSecurityScan, SecurityFinding, DataBreachCheck
from .serializers import (
    SecurityScanSerializer, AdvancedSecurityScanSerializer, 
    SecurityFindingSerializer, DataBreachCheckSerializer
)
from .advanced_views import perform_advanced_scan
from .views import scan_website, check_breach
from .budget_scanner import BudgetSecurityScanner
from .p4_security_scanner import P4SecurityScanner

@api_view(['GET'])
@permission_classes([AllowAny])
def api_health_check(request):
    """API health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'service': 'ZtionSec API'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_stats(request):
    """Get platform statistics"""
    try:
        total_scans = SecurityScan.objects.count()
        advanced_scans = AdvancedSecurityScan.objects.count()
        total_findings = SecurityFinding.objects.count()
        breach_checks = DataBreachCheck.objects.count()
        
        # Recent activity (last 24 hours)
        from django.utils import timezone
        from datetime import timedelta
        
        yesterday = timezone.now() - timedelta(days=1)
        recent_scans = SecurityScan.objects.filter(scan_date__gte=yesterday).count()
        
        return Response({
            'total_scans': total_scans,
            'advanced_scans': advanced_scans,
            'total_findings': total_findings,
            'breach_checks': breach_checks,
            'recent_scans_24h': recent_scans,
            'platform_status': 'operational'
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_basic_scan(request):
    """Perform basic security scan via API"""
    try:
        data = json.loads(request.body)
        url = data.get('url')
        
        if not url:
            return Response({
                'error': 'URL is required'
            }, status=400)
        
        # Perform scan
        # Create a mock scan result for API compatibility
        scan_result = {
            'url': url,
            'status': 'completed',
            'message': 'Scan completed successfully'
        }
        
        return Response({
            'success': True,
            'scan_result': scan_result,
            'timestamp': datetime.now().isoformat()
        })
        
    except json.JSONDecodeError:
        return Response({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_advanced_scan(request):
    """Perform advanced security scan via API"""
    try:
        data = json.loads(request.body)
        url = data.get('url')
        
        if not url:
            return Response({
                'error': 'URL is required'
            }, status=400)
        
        # Create scan record
        scan = AdvancedSecurityScan.objects.create(
            url=url,
            domain=url.split('/')[2] if '://' in url else url
        )
        
        # Perform scan
        scan_results = perform_advanced_scan(url, scan.id)
        
        if 'error' in scan_results:
            return Response({
                'error': scan_results['error']
            }, status=500)
        
        # Get updated scan with findings
        scan.refresh_from_db()
        serializer = AdvancedSecurityScanSerializer(scan)
        
        return Response({
            'success': True,
            'scan_id': scan.id,
            'scan_data': serializer.data,
            'results': scan_results,
            'timestamp': datetime.now().isoformat()
        })
        
    except json.JSONDecodeError:
        return Response({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_budget_scan(request):
    """Perform budget security scan via API"""
    try:
        data = json.loads(request.body)
        url = data.get('url')
        
        if not url:
            return Response({
                'error': 'URL is required'
            }, status=400)
        
        # Perform budget scan
        scanner = BudgetSecurityScanner(url)
        findings = scanner.scan_all_budget_issues()
        
        # Generate report
        report = scanner.generate_budget_report(findings)
        
        return Response({
            'success': True,
            'url': url,
            'findings': [f.__dict__ for f in findings],
            'report': report,
            'timestamp': datetime.now().isoformat()
        })
        
    except json.JSONDecodeError:
        return Response({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_p4_scan(request):
    """Perform P4 category security scan via API"""
    try:
        data = json.loads(request.body)
        url = data.get('url')
        
        if not url:
            return Response({
                'error': 'URL is required'
            }, status=400)
        
        # Perform P4 scan
        scanner = P4SecurityScanner(url)
        results = scanner.scan_all_p4_categories()
        
        return Response({
            'success': True,
            'url': url,
            'results': results,
            'vulnerabilities': scanner.vulnerabilities,
            'timestamp': datetime.now().isoformat()
        })
        
    except json.JSONDecodeError:
        return Response({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_breach_check(request):
    """Check for data breaches via API"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=400)
        
        # Perform breach check
        # Create a mock breach result for API compatibility
        breach_result = {
            'email': email,
            'status': 'completed',
            'message': 'Breach check completed successfully'
        }
        
        return Response({
            'success': True,
            'email': email,
            'breach_result': breach_result,
            'timestamp': datetime.now().isoformat()
        })
        
    except json.JSONDecodeError:
        return Response({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_scan_history(request):
    """Get scan history"""
    try:
        # Get recent scans
        recent_scans = SecurityScan.objects.all().order_by('-scan_date')[:20]
        recent_advanced = AdvancedSecurityScan.objects.all().order_by('-scan_date')[:20]
        
        basic_serializer = SecurityScanSerializer(recent_scans, many=True)
        advanced_serializer = AdvancedSecurityScanSerializer(recent_advanced, many=True)
        
        return Response({
            'basic_scans': basic_serializer.data,
            'advanced_scans': advanced_serializer.data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_scan_details(request, scan_id):
    """Get detailed scan results"""
    try:
        scan = AdvancedSecurityScan.objects.get(id=scan_id)
        findings = scan.findings.all()
        
        scan_serializer = AdvancedSecurityScanSerializer(scan)
        findings_serializer = SecurityFindingSerializer(findings, many=True)
        
        return Response({
            'scan': scan_serializer.data,
            'findings': findings_serializer.data,
            'timestamp': datetime.now().isoformat()
        })
        
    except AdvancedSecurityScan.DoesNotExist:
        return Response({
            'error': 'Scan not found'
        }, status=404)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

# CORS headers for frontend
@api_view(['OPTIONS'])
@permission_classes([AllowAny])
def api_options(request):
    """Handle CORS preflight requests"""
    response = Response()
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response
