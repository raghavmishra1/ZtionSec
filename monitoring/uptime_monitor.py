"""
Free Website Monitoring Script for ZtionSec
Monitors website uptime, response time, and basic health checks
"""

import requests
import time
import json
import smtplib
from email.mime.text import MimeText
from datetime import datetime
import os
from typing import Dict, List

class WebsiteMonitor:
    def __init__(self, config_file='monitoring_config.json'):
        self.config = self.load_config(config_file)
        self.alerts_sent = {}
        
    def load_config(self, config_file: str) -> Dict:
        """Load monitoring configuration"""
        default_config = {
            "websites": [
                {
                    "name": "ZtionSec Main",
                    "url": "https://your-ztionsec-app.onrender.com",
                    "expected_status": 200,
                    "timeout": 30,
                    "check_interval": 300  # 5 minutes
                }
            ],
            "notifications": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "your-email@gmail.com",
                    "password": "your-app-password",
                    "to_email": "alerts@yourdomain.com"
                },
                "webhook": {
                    "enabled": False,
                    "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
                }
            },
            "thresholds": {
                "response_time_warning": 5.0,  # seconds
                "response_time_critical": 10.0,
                "consecutive_failures": 3
            }
        }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            # Create default config file
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default config file: {config_file}")
            return default_config
    
    def check_website(self, website: Dict) -> Dict:
        """Check a single website"""
        result = {
            'name': website['name'],
            'url': website['url'],
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'response_time': None,
            'status_code': None,
            'error': None
        }
        
        try:
            start_time = time.time()
            response = requests.get(
                website['url'], 
                timeout=website.get('timeout', 30),
                headers={'User-Agent': 'ZtionSec-Monitor/1.0'}
            )
            response_time = time.time() - start_time
            
            result.update({
                'status': 'up' if response.status_code == website.get('expected_status', 200) else 'down',
                'response_time': round(response_time, 2),
                'status_code': response.status_code
            })
            
            # Check response time thresholds
            if response_time > self.config['thresholds']['response_time_critical']:
                result['status'] = 'critical'
            elif response_time > self.config['thresholds']['response_time_warning']:
                result['status'] = 'warning'
                
        except requests.exceptions.RequestException as e:
            result.update({
                'status': 'down',
                'error': str(e)
            })
        
        return result
    
    def send_email_alert(self, subject: str, body: str):
        """Send email alert"""
        if not self.config['notifications']['email']['enabled']:
            return
            
        try:
            email_config = self.config['notifications']['email']
            msg = MimeText(body)
            msg['Subject'] = subject
            msg['From'] = email_config['username']
            msg['To'] = email_config['to_email']
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"Email alert sent: {subject}")
        except Exception as e:
            print(f"Failed to send email alert: {e}")
    
    def send_webhook_alert(self, data: Dict):
        """Send webhook alert (Slack, Discord, etc.)"""
        if not self.config['notifications']['webhook']['enabled']:
            return
            
        try:
            webhook_url = self.config['notifications']['webhook']['url']
            
            # Format for Slack
            slack_data = {
                "text": f"🚨 ZtionSec Alert: {data['name']}",
                "attachments": [
                    {
                        "color": "danger" if data['status'] == 'down' else "warning",
                        "fields": [
                            {"title": "Status", "value": data['status'], "short": True},
                            {"title": "URL", "value": data['url'], "short": True},
                            {"title": "Response Time", "value": f"{data.get('response_time', 'N/A')}s", "short": True},
                            {"title": "Status Code", "value": str(data.get('status_code', 'N/A')), "short": True},
                            {"title": "Timestamp", "value": data['timestamp'], "short": False}
                        ]
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=slack_data, timeout=10)
            if response.status_code == 200:
                print(f"Webhook alert sent for {data['name']}")
            else:
                print(f"Failed to send webhook alert: {response.status_code}")
                
        except Exception as e:
            print(f"Failed to send webhook alert: {e}")
    
    def log_result(self, result: Dict):
        """Log monitoring result"""
        log_file = f"monitoring_log_{datetime.now().strftime('%Y%m')}.json"
        
        try:
            # Read existing logs
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Add new result
            logs.append(result)
            
            # Keep only last 1000 entries to manage file size
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # Write back to file
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Failed to log result: {e}")
    
    def monitor_websites(self):
        """Monitor all configured websites"""
        print(f"🔍 Starting website monitoring at {datetime.now()}")
        
        for website in self.config['websites']:
            result = self.check_website(website)
            
            # Log result
            self.log_result(result)
            
            # Print status
            status_emoji = {
                'up': '✅',
                'down': '❌',
                'warning': '⚠️',
                'critical': '🚨'
            }
            
            print(f"{status_emoji.get(result['status'], '❓')} {result['name']}: "
                  f"{result['status']} ({result.get('response_time', 'N/A')}s)")
            
            # Send alerts if needed
            if result['status'] in ['down', 'critical']:
                alert_key = f"{website['name']}_{result['status']}"
                
                # Avoid spam - only alert once per hour for same issue
                last_alert = self.alerts_sent.get(alert_key, 0)
                if time.time() - last_alert > 3600:  # 1 hour
                    subject = f"🚨 ZtionSec Alert: {website['name']} is {result['status']}"
                    body = f"""
Website: {website['name']}
URL: {website['url']}
Status: {result['status']}
Response Time: {result.get('response_time', 'N/A')}s
Status Code: {result.get('status_code', 'N/A')}
Error: {result.get('error', 'None')}
Timestamp: {result['timestamp']}

Please check your ZtionSec deployment immediately.
                    """
                    
                    self.send_email_alert(subject, body)
                    self.send_webhook_alert(result)
                    self.alerts_sent[alert_key] = time.time()
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring loop"""
        print("🚀 Starting continuous monitoring...")
        
        while True:
            try:
                self.monitor_websites()
                
                # Wait for next check
                check_interval = min([w.get('check_interval', 300) for w in self.config['websites']])
                print(f"⏰ Next check in {check_interval} seconds...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    monitor = WebsiteMonitor()
    
    # Run single check
    if len(os.sys.argv) > 1 and os.sys.argv[1] == '--once':
        monitor.monitor_websites()
    else:
        # Run continuous monitoring
        monitor.run_continuous_monitoring()
