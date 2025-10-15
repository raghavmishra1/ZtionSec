#!/usr/bin/env python3
"""
Super Aggressive Keep-Alive for ZtionSec Render Service
Prevents cold starts with multiple strategies and real-time monitoring
"""

import requests
import time
import logging
import threading
import json
from datetime import datetime, timezone
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('keepalive.log')
    ]
)
logger = logging.getLogger(__name__)

class SuperAggressiveKeepAlive:
    def __init__(self):
        # Your actual Render service URL
        self.service_url = "https://ztionsec-security-platform.onrender.com"
        
        # Multiple endpoints to keep warm
        self.endpoints = {
            'health': f"{self.service_url}/api/v1/health/",
            'stats': f"{self.service_url}/api/v1/stats/",
            'scan_history': f"{self.service_url}/api/v1/scan-history/",
            'main': f"{self.service_url}/",
        }
        
        # Timing configuration - AGGRESSIVE
        self.ping_interval = 180  # 3 minutes (very aggressive)
        self.burst_interval = 60  # 1 minute burst mode
        self.timeout = 45
        
        # Monitoring stats
        self.stats = {
            'total_pings': 0,
            'successful_pings': 0,
            'failed_pings': 0,
            'consecutive_failures': 0,
            'last_success': None,
            'service_status': 'unknown'
        }
        
        # Threading
        self.running = True
        self.burst_mode = False
    
    def ping_endpoint(self, name, url):
        """Ping a single endpoint with detailed logging"""
        try:
            headers = {
                'User-Agent': 'ZtionSec-SuperAggressiveKeepAlive/2.0',
                'Accept': 'application/json',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
            
            start_time = time.time()
            response = requests.get(url, timeout=self.timeout, headers=headers)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                logger.info(f"✅ {name.upper()}: SUCCESS ({response_time:.0f}ms)")
                
                # Try to parse JSON for additional info
                try:
                    data = response.json()
                    if 'response_time_ms' in data:
                        logger.info(f"   📊 Server response time: {data['response_time_ms']}ms")
                    if 'database' in data:
                        logger.info(f"   🗄️  Database: {data['database']}")
                except:
                    pass
                
                return True
            else:
                logger.warning(f"⚠️ {name.upper()}: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ {name.upper()}: TIMEOUT ({self.timeout}s)")
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ {name.upper()}: CONNECTION ERROR (service sleeping?)")
            return False
        except Exception as e:
            logger.error(f"❌ {name.upper()}: ERROR - {str(e)}")
            return False
    
    def parallel_ping_all_endpoints(self):
        """Ping all endpoints in parallel for faster results"""
        logger.info("🎯 PARALLEL PING: Starting simultaneous endpoint checks...")
        
        success_count = 0
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all ping tasks
            future_to_endpoint = {
                executor.submit(self.ping_endpoint, name, url): name 
                for name, url in self.endpoints.items()
            }
            
            # Collect results
            for future in as_completed(future_to_endpoint):
                endpoint_name = future_to_endpoint[future]
                try:
                    success = future.result()
                    if success:
                        success_count += 1
                except Exception as e:
                    logger.error(f"❌ {endpoint_name}: Exception - {str(e)}")
        
        success_rate = (success_count / len(self.endpoints)) * 100
        logger.info(f"📈 PARALLEL RESULT: {success_count}/{len(self.endpoints)} endpoints successful ({success_rate:.0f}%)")
        
        return success_count > 0
    
    def aggressive_wake_sequence(self):
        """Super aggressive wake-up sequence for sleeping service"""
        logger.info("🔥 AGGRESSIVE WAKE SEQUENCE: Service appears to be sleeping!")
        
        # Phase 1: Rapid fire health checks
        logger.info("   Phase 1: Rapid fire health checks...")
        for i in range(5):
            logger.info(f"      Rapid attempt {i+1}/5")
            if self.ping_endpoint('health-rapid', self.endpoints['health']):
                logger.info("   ✅ Service woke up in Phase 1!")
                return True
            time.sleep(5)
        
        # Phase 2: Multiple endpoint bombardment
        logger.info("   Phase 2: Multiple endpoint bombardment...")
        for i in range(3):
            logger.info(f"      Bombardment round {i+1}/3")
            success = self.parallel_ping_all_endpoints()
            if success:
                logger.info("   ✅ Service woke up in Phase 2!")
                return True
            time.sleep(10)
        
        # Phase 3: Extended timeout attempts
        logger.info("   Phase 3: Extended timeout attempts...")
        original_timeout = self.timeout
        self.timeout = 90  # 90 second timeout
        
        for i in range(2):
            logger.info(f"      Extended attempt {i+1}/2 (90s timeout)")
            if self.ping_endpoint('health-extended', self.endpoints['health']):
                logger.info("   ✅ Service woke up in Phase 3!")
                self.timeout = original_timeout
                return True
            time.sleep(15)
        
        self.timeout = original_timeout
        logger.error("   ❌ All wake-up attempts failed!")
        return False
    
    def perform_keepalive_cycle(self):
        """Perform one complete keep-alive cycle"""
        cycle_start = time.time()
        logger.info("=" * 60)
        logger.info(f"🚀 KEEP-ALIVE CYCLE START: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Update stats
        self.stats['total_pings'] += 1
        
        # Try parallel ping first
        success = self.parallel_ping_all_endpoints()
        
        if success:
            self.stats['successful_pings'] += 1
            self.stats['consecutive_failures'] = 0
            self.stats['last_success'] = datetime.now()
            self.stats['service_status'] = 'active'
            
            # Exit burst mode if we were in it
            if self.burst_mode:
                logger.info("🎉 Exiting burst mode - service is stable")
                self.burst_mode = False
        else:
            self.stats['failed_pings'] += 1
            self.stats['consecutive_failures'] += 1
            self.stats['service_status'] = 'sleeping'
            
            # Try aggressive wake sequence
            logger.info("⚡ Service not responding - initiating aggressive wake sequence...")
            wake_success = self.aggressive_wake_sequence()
            
            if wake_success:
                self.stats['successful_pings'] += 1
                self.stats['consecutive_failures'] = 0
                self.stats['last_success'] = datetime.now()
                self.stats['service_status'] = 'active'
            else:
                # Enter burst mode
                if not self.burst_mode:
                    logger.warning("🚨 ENTERING BURST MODE: Will ping every 60 seconds")
                    self.burst_mode = True
        
        # Log statistics
        cycle_time = time.time() - cycle_start
        success_rate = (self.stats['successful_pings'] / self.stats['total_pings']) * 100
        
        logger.info(f"📊 CYCLE STATS:")
        logger.info(f"   Success Rate: {success_rate:.1f}% ({self.stats['successful_pings']}/{self.stats['total_pings']})")
        logger.info(f"   Consecutive Failures: {self.stats['consecutive_failures']}")
        logger.info(f"   Service Status: {self.stats['service_status'].upper()}")
        logger.info(f"   Cycle Duration: {cycle_time:.1f}s")
        logger.info(f"   Last Success: {self.stats['last_success'] or 'Never'}")
        
        # Alert on persistent failures
        if self.stats['consecutive_failures'] >= 5:
            logger.error(f"🚨 ALERT: Service has failed {self.stats['consecutive_failures']} consecutive times!")
        
        return success
    
    def run_continuous(self):
        """Run the super aggressive keep-alive service continuously"""
        logger.info("🚀 STARTING SUPER AGGRESSIVE KEEP-ALIVE SERVICE")
        logger.info(f"🎯 Target: {self.service_url}")
        logger.info(f"⏰ Normal Interval: {self.ping_interval}s ({self.ping_interval/60:.1f} minutes)")
        logger.info(f"🔥 Burst Interval: {self.burst_interval}s ({self.burst_interval/60:.1f} minutes)")
        logger.info("=" * 60)
        
        try:
            while self.running:
                # Perform keep-alive cycle
                self.perform_keepalive_cycle()
                
                # Determine sleep interval
                sleep_interval = self.burst_interval if self.burst_mode else self.ping_interval
                
                logger.info(f"😴 Sleeping for {sleep_interval}s...")
                logger.info("=" * 60)
                
                # Sleep with ability to interrupt
                for _ in range(sleep_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("🛑 Keep-Alive service stopped by user")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
        finally:
            self.running = False
            logger.info("🏁 Super Aggressive Keep-Alive service terminated")
    
    def run_single_test(self):
        """Run a single comprehensive test"""
        logger.info("🧪 RUNNING SINGLE COMPREHENSIVE TEST")
        logger.info("=" * 60)
        
        success = self.perform_keepalive_cycle()
        
        logger.info("=" * 60)
        logger.info(f"🏁 TEST RESULT: {'SUCCESS' if success else 'FAILED'}")
        
        return success
    
    def get_status_report(self):
        """Generate a detailed status report"""
        report = {
            'service_url': self.service_url,
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats.copy(),
            'burst_mode': self.burst_mode,
            'running': self.running
        }
        
        if self.stats['last_success']:
            report['stats']['last_success'] = self.stats['last_success'].isoformat()
        
        return report

def main():
    """Main function with command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Super Aggressive Keep-Alive for ZtionSec')
    parser.add_argument('--test', action='store_true', help='Run single test')
    parser.add_argument('--interval', type=int, default=180, help='Normal ping interval in seconds')
    parser.add_argument('--burst-interval', type=int, default=60, help='Burst mode interval in seconds')
    parser.add_argument('--status', action='store_true', help='Show status report and exit')
    
    args = parser.parse_args()
    
    service = SuperAggressiveKeepAlive()
    service.ping_interval = args.interval
    service.burst_interval = args.burst_interval
    
    if args.test:
        success = service.run_single_test()
        sys.exit(0 if success else 1)
    elif args.status:
        report = service.get_status_report()
        print(json.dumps(report, indent=2))
    else:
        service.run_continuous()

if __name__ == "__main__":
    main()
