#!/usr/bin/env python3
"""
Aggressive Keep-Alive Service for Render Cold Start Prevention
Multiple endpoint pinging with intelligent timing
"""

import requests
import time
import logging
import json
import threading
from datetime import datetime, timezone
import os
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AggressiveKeepAlive:
    def __init__(self, service_url=None):
        # Your Render service URL - UPDATE THIS WITH YOUR ACTUAL URL
        self.service_url = service_url or "https://ztionsec-api.onrender.com"
        
        # Multiple endpoints to ping
        self.endpoints = {
            'health': f"{self.service_url}/api/v1/health/",
            'stats': f"{self.service_url}/api/v1/stats/",
            'scan_history': f"{self.service_url}/api/v1/scan-history/",
        }
        
        # Aggressive timing configuration
        self.primary_interval = 300    # 5 minutes (more frequent)
        self.secondary_interval = 600  # 10 minutes
        self.burst_interval = 60      # 1 minute during burst mode
        self.timeout = 15             # Shorter timeout
        
        # Monitoring
        self.consecutive_failures = 0
        self.max_failures = 2  # More sensitive
        self.total_requests = 0
        self.successful_requests = 0
        self.burst_mode = False
        self.last_success_time = None
        
    def ping_endpoint(self, name, url):
        """Ping a specific endpoint"""
        try:
            headers = {
                'User-Agent': f'ZtionSec-AggressiveKeepAlive/2.0-{name}',
                'Accept': 'application/json',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, timeout=self.timeout, headers=headers)
            self.total_requests += 1
            
            if response.status_code == 200:
                self.successful_requests += 1
                self.consecutive_failures = 0
                self.last_success_time = datetime.now(timezone.utc)
                
                # Extract response time if available
                try:
                    data = response.json()
                    response_time = data.get('response_time_ms', 'N/A')
                    logger.info(f"✅ {name.upper()} OK - {response_time}ms")
                except:
                    logger.info(f"✅ {name.upper()} OK - {response.elapsed.total_seconds()*1000:.1f}ms")
                
                return True
            else:
                logger.warning(f"⚠️ {name.upper()} returned {response.status_code}")
                self.consecutive_failures += 1
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ {name.upper()} timeout")
            self.consecutive_failures += 1
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ {name.upper()} connection error - service sleeping!")
            self.consecutive_failures += 1
            return False
        except Exception as e:
            logger.error(f"❌ {name.upper()} error: {str(e)}")
            self.consecutive_failures += 1
            return False
    
    def burst_ping_sequence(self):
        """Aggressive burst pinging when service is detected as sleeping"""
        logger.warning("🚨 BURST MODE ACTIVATED - Service appears to be sleeping!")
        self.burst_mode = True
        
        for attempt in range(5):  # 5 burst attempts
            logger.info(f"🔥 Burst attempt {attempt + 1}/5")
            
            # Ping all endpoints rapidly
            for name, url in self.endpoints.items():
                success = self.ping_endpoint(name, url)
                if success:
                    logger.info("✅ Service is awake! Exiting burst mode.")
                    self.burst_mode = False
                    return True
                time.sleep(2)  # 2 second delay between burst pings
            
            if attempt < 4:  # Don't sleep after last attempt
                time.sleep(self.burst_interval)
        
        logger.warning("⚠️ Burst mode completed - service may still be sleeping")
        self.burst_mode = False
        return False
    
    def intelligent_ping_sequence(self):
        """Intelligent pinging with multiple endpoints"""
        current_time = datetime.now(timezone.utc)
        
        # Check if we need burst mode
        if self.consecutive_failures >= self.max_failures:
            return self.burst_ping_sequence()
        
        # Normal pinging sequence
        logger.info(f"🏥 Starting ping sequence at {current_time.strftime('%H:%M:%S UTC')}")
        
        success_count = 0
        for name, url in self.endpoints.items():
            success = self.ping_endpoint(name, url)
            if success:
                success_count += 1
            time.sleep(1)  # Small delay between endpoint pings
        
        # Calculate success rate
        total_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        sequence_rate = (success_count / len(self.endpoints) * 100)
        
        logger.info(f"📊 Sequence: {success_count}/{len(self.endpoints)} | Overall: {total_rate:.1f}%")
        
        return success_count > 0
    
    def get_dynamic_interval(self):
        """Calculate dynamic ping interval based on service health"""
        if self.burst_mode:
            return self.burst_interval
        
        # If we've had recent failures, ping more frequently
        if self.consecutive_failures > 0:
            return self.primary_interval
        
        # If service is healthy, use normal interval
        return self.secondary_interval
    
    def run_continuous_aggressive(self):
        """Run aggressive keep-alive service"""
        logger.info("🚀 Starting AGGRESSIVE Keep-Alive Service")
        logger.info(f"🎯 Target: {self.service_url}")
        logger.info(f"📡 Endpoints: {len(self.endpoints)}")
        logger.info(f"⏰ Primary interval: {self.primary_interval}s")
        logger.info(f"⚡ Burst interval: {self.burst_interval}s")
        
        while True:
            try:
                # Perform intelligent ping sequence
                self.intelligent_ping_sequence()
                
                # Get dynamic interval
                interval = self.get_dynamic_interval()
                
                # Add some randomization to avoid predictable patterns
                jitter = random.randint(-30, 30)  # ±30 seconds
                actual_interval = max(60, interval + jitter)  # Minimum 1 minute
                
                logger.info(f"😴 Next ping in {actual_interval}s...")
                logger.info("-" * 60)
                
                time.sleep(actual_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Aggressive Keep-Alive stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {str(e)}")
                time.sleep(60)
    
    def run_background_thread(self):
        """Run keep-alive in background thread"""
        def background_worker():
            self.run_continuous_aggressive()
        
        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()
        logger.info("🔄 Background keep-alive thread started")
        return thread

def create_github_action_keepalive():
    """Create GitHub Action for external keep-alive"""
    github_action = """name: Aggressive ZtionSec Keep-Alive

on:
  schedule:
    # Every 5 minutes
    - cron: '*/5 * * * *'
  workflow_dispatch:

jobs:
  aggressive-keepalive:
    runs-on: ubuntu-latest
    steps:
      - name: Ping Health Endpoint
        run: |
          curl -f -m 10 https://your-ztionsec-api.onrender.com/api/v1/health/ || echo "Health check failed"
      
      - name: Ping Stats Endpoint  
        run: |
          curl -f -m 10 https://your-ztionsec-api.onrender.com/api/v1/stats/ || echo "Stats check failed"
      
      - name: Ping Scan History
        run: |
          curl -f -m 10 https://your-ztionsec-api.onrender.com/api/v1/scan-history/ || echo "History check failed"
      
      - name: Burst Mode (if needed)
        run: |
          for i in {1..3}; do
            echo "Burst ping $i"
            curl -f -m 5 https://your-ztionsec-api.onrender.com/api/v1/health/ && break
            sleep 10
          done
"""
    
    return github_action

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggressive Keep-Alive for ZtionSec')
    parser.add_argument('--url', help='Service URL to ping')
    parser.add_argument('--test', action='store_true', help='Run single test')
    parser.add_argument('--github-action', action='store_true', help='Generate GitHub Action YAML')
    parser.add_argument('--primary-interval', type=int, default=300, help='Primary ping interval')
    parser.add_argument('--burst-interval', type=int, default=60, help='Burst mode interval')
    
    args = parser.parse_args()
    
    if args.github_action:
        print("GitHub Action YAML:")
        print("=" * 50)
        print(create_github_action_keepalive())
        return
    
    service = AggressiveKeepAlive(service_url=args.url)
    service.primary_interval = args.primary_interval
    service.burst_interval = args.burst_interval
    
    if args.test:
        success = service.intelligent_ping_sequence()
        exit(0 if success else 1)
    else:
        service.run_continuous_aggressive()

if __name__ == "__main__":
    main()
