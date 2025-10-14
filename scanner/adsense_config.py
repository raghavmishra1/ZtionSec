"""
Google AdSense Configuration for ZtionSec
Publisher ID: pub-9693358517951567
"""

import os
from django.conf import settings

class AdSenseConfig:
    """AdSense configuration and management"""
    
    # Your AdSense Publisher ID
    PUBLISHER_ID = "pub-9693358517951567"
    
    # Ad Unit Slots (Real AdSense account slots)
    AD_SLOTS = {
        'header_banner': '6305965263',      # 728x90 Header Banner (Ztion)
        'sidebar_medium': '6305965263',     # 300x250 Sidebar Rectangle (Ztion)
        'footer_banner': '6305965263',      # 728x90 Footer Banner (Ztion)
        'in_article': '6305965263',         # In-Article Fluid Ad (Ztion)
        'responsive': '6305965263',         # Responsive Ad Unit (Ztion)
        'mobile_banner': '6305965263',      # 320x100 Mobile Banner (Ztion)
        'ztion_main': '6305965263',         # Main Ztion Ad Unit
    }
    
    # AdSense Script URL
    ADSENSE_SCRIPT_URL = f"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-{PUBLISHER_ID}"
    
    @classmethod
    def get_ad_code(cls, slot_name, width=None, height=None, responsive=False):
        """Generate AdSense ad code for a specific slot"""
        if slot_name not in cls.AD_SLOTS:
            return ""
        
        slot_id = cls.AD_SLOTS[slot_name]
        
        if responsive:
            return f'''
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-{cls.PUBLISHER_ID}"
                 data-ad-slot="{slot_id}"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>
                 (adsbygoogle = window.adsbygoogle || []).push({{}});
            </script>
            '''
        else:
            style = f"display:inline-block;width:{width}px;height:{height}px" if width and height else "display:block"
            return f'''
            <ins class="adsbygoogle"
                 style="{style}"
                 data-ad-client="ca-{cls.PUBLISHER_ID}"
                 data-ad-slot="{slot_id}"></ins>
            <script>
                 (adsbygoogle = window.adsbygoogle || []).push({{}});
            </script>
            '''
    
    @classmethod
    def get_auto_ads_code(cls):
        """Get Auto Ads code (recommended for maximum revenue)"""
        return f'''
        <script async src="{cls.ADSENSE_SCRIPT_URL}" crossorigin="anonymous"></script>
        '''
    
    @classmethod
    def is_enabled(cls):
        """Check if AdSense is enabled"""
        return getattr(settings, 'ADSENSE_ENABLED', True)
    
    @classmethod
    def should_show_ads(cls, request):
        """Determine if ads should be shown based on various factors"""
        # Don't show ads in development unless explicitly enabled
        if settings.DEBUG and not getattr(settings, 'ADSENSE_DEBUG', False):
            return False
        
        # Don't show ads to admin users (optional)
        if hasattr(request, 'user') and request.user.is_staff:
            return getattr(settings, 'ADSENSE_SHOW_TO_STAFF', True)
        
        return cls.is_enabled()

# Template context processor to make AdSense available in templates
def adsense_context(request):
    """Add AdSense configuration to template context"""
    return {
        'adsense': {
            'enabled': AdSenseConfig.should_show_ads(request),
            'publisher_id': AdSenseConfig.PUBLISHER_ID,
            'script_url': AdSenseConfig.ADSENSE_SCRIPT_URL,
            'slots': AdSenseConfig.AD_SLOTS,
        }
    }

# Pre-defined ad units for easy use
HEADER_BANNER_AD = AdSenseConfig.get_ad_code('header_banner', 728, 90)
SIDEBAR_AD = AdSenseConfig.get_ad_code('sidebar_medium', 300, 250)
FOOTER_BANNER_AD = AdSenseConfig.get_ad_code('footer_banner', 728, 90)
IN_ARTICLE_AD = AdSenseConfig.get_ad_code('in_article')
RESPONSIVE_AD = AdSenseConfig.get_ad_code('responsive', responsive=True)
MOBILE_BANNER_AD = AdSenseConfig.get_ad_code('mobile_banner', 320, 100)
