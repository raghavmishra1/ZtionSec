"""
Template tags for Google AdSense integration
"""

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from scanner.adsense_config import AdSenseConfig

register = template.Library()

@register.simple_tag(takes_context=True)
def adsense_auto_ads(context):
    """Include AdSense Auto Ads script"""
    request = context['request']
    if not AdSenseConfig.should_show_ads(request):
        return ""
    
    return mark_safe(AdSenseConfig.get_auto_ads_code())

@register.simple_tag(takes_context=True)
def adsense_ad(context, slot_name, width=None, height=None, responsive=False):
    """Display an AdSense ad unit"""
    request = context['request']
    if not AdSenseConfig.should_show_ads(request):
        return ""
    
    ad_code = AdSenseConfig.get_ad_code(slot_name, width, height, responsive)
    return mark_safe(ad_code)

@register.simple_tag(takes_context=True)
def adsense_header_banner(context):
    """Display header banner ad (728x90)"""
    request = context['request']
    if not AdSenseConfig.should_show_ads(request):
        return ""
    
    return mark_safe(f'''
    <div class="adsense-banner-header">
        {AdSenseConfig.get_ad_code('header_banner', 728, 90)}
    </div>
    ''')

@register.simple_tag(takes_context=True)
def adsense_sidebar(context):
    """Display sidebar ad (300x250)"""
    request = context['request']
    if not AdSenseConfig.should_show_ads(request):
        return ""
    
    return mark_safe(f'''
    <div class="adsense-sidebar">
        {AdSenseConfig.get_ad_code('sidebar_medium', 300, 250)}
    </div>
    ''')

@register.simple_tag(takes_context=True)
def adsense_footer_banner(context):
    """Display footer banner ad (728x90)"""
    request = context['request']
    if not AdSenseConfig.should_show_ads(request):
        return ""
    
    return mark_safe(f'''
    <div class="adsense-banner-footer">
        {AdSenseConfig.get_ad_code('footer_banner', 728, 90)}
    </div>
    ''')

@register.simple_tag(takes_context=True)
def adsense_in_article(context):
    """Display in-article ad"""
    request = context['request']
    if not AdSenseConfig.should_show_ads(request):
        return ""
    
    return mark_safe(f'''
    <div class="adsense-in-article">
        <ins class="adsbygoogle"
             style="display:block; text-align:center;"
             data-ad-layout="in-article"
             data-ad-format="fluid"
             data-ad-client="ca-{AdSenseConfig.PUBLISHER_ID}"
             data-ad-slot="{AdSenseConfig.AD_SLOTS['in_article']}"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>
    </div>
    ''')

@register.simple_tag(takes_context=True)
def adsense_responsive(context):
    """Display responsive ad"""
    request = context['request']
    if not AdSenseConfig.should_show_ads(request):
        return ""
    
    return mark_safe(f'''
    <div class="adsense-responsive">
        {AdSenseConfig.get_ad_code('responsive', responsive=True)}
    </div>
    ''')

@register.simple_tag(takes_context=True)
def ztion_ad(context):
    """Display the main Ztion AdSense ad unit"""
    request = context['request']
    if not AdSenseConfig.should_show_ads(request):
        return ""
    
    return mark_safe('''
    <div class="ztion-adsense-container">
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-9693358517951567"
             data-ad-slot="6305965263"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>
    ''')

@register.inclusion_tag('adsense/ad_unit.html', takes_context=True)
def adsense_unit(context, slot_name, css_class="", width=None, height=None):
    """Include an AdSense ad unit with template"""
    request = context['request']
    show_ads = AdSenseConfig.should_show_ads(request)
    
    return {
        'show_ads': show_ads,
        'publisher_id': AdSenseConfig.PUBLISHER_ID,
        'slot_id': AdSenseConfig.AD_SLOTS.get(slot_name, ''),
        'css_class': css_class,
        'width': width,
        'height': height,
    }
