#!/usr/bin/env python3
"""
External Keep-Alive Service for ZtionSec
Run this on a separate server/service to ping your Render app
"""

import requests
import time
import logging
import json
from datetime import datetime, timezone
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExternalKeepAlive:
    def __init__(self):
        # Your Render service URL
        self.service_url = "https://ztionsec-api.onrender.com"  # Replace with your actual URL
        self.health_endpoint = f"{self.service_url}/api/v1/health/"
        self.stats_endpoint = f"{self.service_url}/api/v1/stats/"
        
        # Timing configuration
        self.ping_interval = 600  # 10 minutes
        self.timeout = 30
        
        # Monitoring
        self.consecutive_failures = 0
        self.max_failures = 3
        self.total_pings = 0
        self.successful_pings = 0
        
    def ping_health_endpoint(self):
        """Ping the health endpoint"""
        try:
            logger.info(f"🏥 Pinging health endpoint...")
            
            response = requests.get(
                self.health_endpoint,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'ZtionSec-ExternalKeepAlive/1.0',
                    'Accept': 'application/json'
                }
            )
            
            self.total_pings += 1
            
            if response.status_code == 200:
                data = response.json()
                response_time = data.get('response_time_ms', 'N/A')
                db_status = data.get('database', 'unknown')
                
                logger.info(f"✅ Health check successful")
                logger.info(f"   📊 Response time: {response_time}ms")
                logger.info(f"   🗄️  Database: {db_status}")
                
                self.successful_pings += 1
                self.consecutive_failures = 0
                return True
            else:
                logger.warning(f"⚠️ Health check returned status: {response.status_code}")
                self.consecutive_failures += 1
                return False
                
        except requests.exceptions.Timeout:
            logger.error("❌ Health check timed out")
            self.consecutive_failures += 1
            return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ Connection error - service may be sleeping")
            self.consecutive_failures += 1
            return False
        except Exception as e:
            logger.error(f"❌ Health check error: {str(e)}")
            self.consecutive_failures += 1
            return False
    
    def ping_stats_endpoint(self):
        """Ping the stats endpoint for additional warmup"""
        try:
            logger.info(f"📊 Pinging stats endpoint...")
            
            response = requests.get(
                self.stats_endpoint,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'ZtionSec-ExternalKeepAlive/1.0',
                    'Accept': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                total_scans = data.get('total_scans', 0)
                logger.info(f"✅ Stats retrieved - Total scans: {total_scans}")
                return True
            else:
                logger.warning(f"⚠️ Stats endpoint returned status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Stats endpoint error: {str(e)}")
            return False
    
    def perform_warmup_sequence(self):
        """Perform a complete warmup sequence"""
        logger.info("🔥 Starting warmup sequence...")
        
        # Ping health endpoint
        health_success = self.ping_health_endpoint()
        
        # If health is good, ping stats too
        if health_success:
            self.ping_stats_endpoint()
        
        # Calculate success rate
        success_rate = (self.successful_pings / self.total_pings * 100) if self.total_pings > 0 else 0
        
        logger.info(f"📈 Success rate: {success_rate:.1f}% ({self.successful_pings}/{self.total_pings})")
        
        # Check for consecutive failures
        if self.consecutive_failures >= self.max_failures:
            logger.error(f"🚨 Service has failed {self.consecutive_failures} consecutive times!")
            # Here you could implement notifications (email, Slack, etc.)
        
        return health_success
    
    def run_continuous(self):
        """Run the keep-alive service continuously"""
        logger.info("🚀 Starting External Keep-Alive Service")
        logger.info(f"🎯 Target: {self.service_url}")
        logger.info(f"⏰ Interval: {self.ping_interval} seconds ({self.ping_interval/60:.1f} minutes)")
        
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                logger.info(f"⏰ {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                
                self.perform_warmup_sequence()
                
                logger.info(f"😴 Sleeping for {self.ping_interval} seconds...")
                logger.info("-" * 50)
                
                time.sleep(self.ping_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Keep-Alive service stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def run_single_test(self):
        """Run a single test"""
        logger.info("🧪 Running single keep-alive test...")
        return self.perform_warmup_sequence()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='External Keep-Alive Service for ZtionSec')
    parser.add_argument('--test', action='store_true', help='Run single test')
    parser.add_argument('--interval', type=int, default=600, help='Ping interval in seconds')
    
    args = parser.parse_args()
    
    service = ExternalKeepAlive()
    service.ping_interval = args.interval
    
    if args.test:
        success = service.run_single_test()
        exit(0 if success else 1)
    else:
        service.run_continuous()

if __name__ == "__main__":
    main()
