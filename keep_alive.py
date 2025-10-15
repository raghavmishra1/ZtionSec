#!/usr/bin/env python3
"""
Keep-Alive Service for Render Cold Start Prevention
Pings the health endpoint every 10 minutes to prevent service sleep
"""

import requests
import time
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KeepAliveService:
    def __init__(self, service_url=None):
        # Get service URL from environment or use default
        self.service_url = service_url or os.getenv('RENDER_EXTERNAL_URL', 'https://ztionsec-api.onrender.com')
        self.health_endpoint = f"{self.service_url}/api/v1/health/"
        self.ping_interval = 600  # 10 minutes in seconds
        self.timeout = 30  # Request timeout in seconds
        
    def ping_service(self):
        """Send a ping to the health endpoint"""
        try:
            logger.info(f"Pinging service at {self.health_endpoint}")
            
            response = requests.get(
                self.health_endpoint,
                timeout=self.timeout,
                headers={'User-Agent': 'ZtionSec-KeepAlive/1.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                response_time = data.get('response_time_ms', 'N/A')
                logger.info(f"✅ Service is healthy - Response time: {response_time}ms")
                return True
            else:
                logger.warning(f"⚠️ Service returned status code: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("❌ Request timed out")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ Connection error - service may be starting up")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            return False
    
    def run_continuous(self):
        """Run the keep-alive service continuously"""
        logger.info(f"🚀 Starting Keep-Alive service for {self.service_url}")
        logger.info(f"📊 Ping interval: {self.ping_interval} seconds")
        
        consecutive_failures = 0
        max_failures = 5
        
        while True:
            try:
                success = self.ping_service()
                
                if success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    
                if consecutive_failures >= max_failures:
                    logger.error(f"❌ Service failed {max_failures} consecutive times")
                    # Could implement notification here (email, Slack, etc.)
                    consecutive_failures = 0  # Reset counter
                
                # Wait before next ping
                logger.info(f"⏰ Next ping in {self.ping_interval} seconds...")
                time.sleep(self.ping_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Keep-Alive service stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in main loop: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def run_single_ping(self):
        """Run a single ping (useful for testing)"""
        return self.ping_service()

def main():
    """Main function for running the keep-alive service"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ZtionSec Keep-Alive Service')
    parser.add_argument('--url', help='Service URL to ping')
    parser.add_argument('--single', action='store_true', help='Run single ping test')
    parser.add_argument('--interval', type=int, default=600, help='Ping interval in seconds')
    
    args = parser.parse_args()
    
    service = KeepAliveService(service_url=args.url)
    service.ping_interval = args.interval
    
    if args.single:
        success = service.run_single_ping()
        exit(0 if success else 1)
    else:
        service.run_continuous()

if __name__ == "__main__":
    main()
