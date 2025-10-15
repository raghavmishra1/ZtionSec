"""
URL configuration for Ztionsec project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import Http404
from django.views.generic import TemplateView
from scanner import views as scanner_views

# Custom admin site configuration
admin.site.site_header = "ZtionSec Security Administration"
admin.site.site_title = "ZtionSec Admin"
admin.site.index_title = "Security Management Dashboard"

# Security function to block common attack paths
def block_common_attacks(request):
    """Block common attack paths and return 404"""
    raise Http404("Page not found")

urlpatterns = [
    # Custom secure admin URL (hidden from common scanners)
    path('secure-admin-panel-ztionsec-2024/', admin.site.urls),
    
    # Block common attack paths - return 404 instead of revealing system info
    path('admin/', block_common_attacks),
    path('admin', block_common_attacks),
    path('wp-admin/', block_common_attacks),
    path('wp-admin', block_common_attacks),
    path('administrator/', block_common_attacks),
    path('administrator', block_common_attacks),
    path('phpmyadmin/', block_common_attacks),
    path('phpmyadmin', block_common_attacks),
    path('database/', block_common_attacks),
    path('database', block_common_attacks),
    path('.git/', block_common_attacks),
    path('.git', block_common_attacks),
    path('.svn/', block_common_attacks),
    path('.svn', block_common_attacks),
    path('config.php', block_common_attacks),
    path('wp-config.php', block_common_attacks),
    path('.env', block_common_attacks),
    path('phpinfo.php', block_common_attacks),
    path('info.php', block_common_attacks),
    path('test.php', block_common_attacks),
    
    # API URLs (for backend-only deployment)
    path('', include('scanner.api_urls')),
    
    # ads.txt file for Google AdSense
    path('ads.txt', scanner_views.ads_txt, name='ads_txt'),
    
    # Main application URLs
    path('', include('scanner.urls')),
]

# Custom error handlers to prevent information disclosure
handler404 = 'scanner.views.custom_404'
handler500 = 'scanner.views.custom_500'
