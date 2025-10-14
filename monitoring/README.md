# 📊 ZtionSec Monitoring Setup

## 🎯 **Overview**

This directory contains monitoring tools and configurations to keep your ZtionSec deployment healthy and running smoothly.

## 📁 **Files Included**

- `uptime_monitor.py` - Python script for website monitoring
- `monitoring_config.json` - Configuration file for monitoring settings
- `github_actions_monitor.yml` - GitHub Actions workflow for automated monitoring
- `README.md` - This documentation file

## 🚀 **Quick Setup**

### **1. Local Monitoring**

```bash
# Install dependencies
pip install requests

# Configure your URLs
nano monitoring_config.json

# Run single check
python uptime_monitor.py --once

# Run continuous monitoring
python uptime_monitor.py
```

### **2. GitHub Actions Monitoring**

1. Copy `github_actions_monitor.yml` to `.github/workflows/monitor.yml`
2. Add these secrets to your GitHub repository:
   - `WEBSITE_URL` - Your deployed app URL
   - `SLACK_WEBHOOK` - (Optional) Slack webhook for alerts
   - `EMAIL_USERNAME` - (Optional) Email for alerts
   - `EMAIL_PASSWORD` - (Optional) Email app password
   - `EMAIL_TO` - (Optional) Alert recipient email

### **3. Third-Party Services**

#### **UptimeRobot (Free)**
1. Sign up at [uptimerobot.com](https://uptimerobot.com)
2. Add HTTP(s) monitor with your app URL
3. Set 5-minute intervals
4. Configure email/SMS alerts

#### **Pingdom (Free Tier)**
1. Sign up at [pingdom.com](https://pingdom.com)
2. Create uptime check
3. Set alert preferences

## ⚙️ **Configuration**

### **monitoring_config.json**

```json
{
  "websites": [
    {
      "name": "ZtionSec Main",
      "url": "https://your-app.onrender.com",
      "expected_status": 200,
      "timeout": 30,
      "check_interval": 300
    }
  ],
  "notifications": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your-email@gmail.com",
      "password": "your-app-password",
      "to_email": "alerts@yourdomain.com"
    },
    "webhook": {
      "enabled": true,
      "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    }
  },
  "thresholds": {
    "response_time_warning": 5.0,
    "response_time_critical": 10.0,
    "consecutive_failures": 3
  }
}
```

## 📧 **Email Alerts Setup**

### **Gmail Setup**
1. Enable 2-factor authentication
2. Generate app password: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Use app password in configuration

### **Other Email Providers**
- **Outlook**: smtp-mail.outlook.com:587
- **Yahoo**: smtp.mail.yahoo.com:587
- **Custom SMTP**: Use your provider's settings

## 🔔 **Slack Alerts Setup**

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Create new app
3. Add "Incoming Webhooks" feature
4. Create webhook for your channel
5. Copy webhook URL to configuration

## 📈 **Monitoring Features**

### **Uptime Monitoring**
- ✅ HTTP status code checking
- ✅ Response time measurement
- ✅ SSL certificate validation
- ✅ Custom timeout settings

### **Performance Monitoring**
- ✅ Response time tracking
- ✅ Performance degradation alerts
- ✅ Historical data logging
- ✅ Trend analysis

### **Security Monitoring**
- ✅ Security headers validation
- ✅ SSL certificate expiry
- ✅ Vulnerability scanning
- ✅ Compliance checking

### **Alert System**
- ✅ Email notifications
- ✅ Slack/Discord webhooks
- ✅ SMS alerts (via third-party)
- ✅ Custom webhook support

## 📊 **Monitoring Dashboard**

### **Simple Status Page**
Create a basic status page for your users:

```python
# views.py
def status_page(request):
    return render(request, 'status.html', {
        'status': 'operational',
        'uptime': '99.9%',
        'last_incident': 'None',
        'response_time': '150ms'
    })
```

### **Health Check Endpoint**
```python
# urls.py
path('health/', health_check, name='health_check'),

# views.py
def health_check(request):
    try:
        # Test database
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected',
            'version': '1.0.0'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Email Not Sending**
- Check SMTP settings
- Verify app password (not regular password)
- Ensure 2FA is enabled for Gmail
- Check firewall/network restrictions

#### **Webhook Failures**
- Verify webhook URL is correct
- Check webhook service status
- Test webhook manually with curl
- Review webhook payload format

#### **Monitoring Script Errors**
- Check Python version (3.7+)
- Install required packages: `pip install requests`
- Verify network connectivity
- Check file permissions

### **Debug Commands**

```bash
# Test email configuration
python -c "
import smtplib
from email.mime.text import MimeText
# Test your SMTP settings here
"

# Test webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert"}' \
  YOUR_WEBHOOK_URL

# Test website connectivity
curl -I https://your-app.onrender.com
```

## 📋 **Monitoring Checklist**

- [ ] ✅ **Uptime monitoring configured**
- [ ] ✅ **Response time alerts set**
- [ ] ✅ **Email notifications working**
- [ ] ✅ **Webhook alerts configured**
- [ ] ✅ **SSL certificate monitoring**
- [ ] ✅ **Database connectivity checks**
- [ ] ✅ **Security headers validation**
- [ ] ✅ **Performance baselines established**
- [ ] ✅ **Incident response plan ready**
- [ ] ✅ **Backup monitoring system**

## 🎯 **Best Practices**

1. **Multiple Monitoring Sources**: Use both internal scripts and external services
2. **Redundant Alerts**: Configure multiple notification channels
3. **Baseline Metrics**: Establish normal performance baselines
4. **Regular Testing**: Test monitoring systems monthly
5. **Documentation**: Keep monitoring procedures documented
6. **Escalation**: Define escalation procedures for critical issues

## 📞 **Support**

For monitoring setup help:
1. Check the main deployment guide
2. Review GitHub Issues
3. Test configurations locally first
4. Use debug commands for troubleshooting

**Keep your ZtionSec platform monitored and healthy! 🚀**
