# Gunicorn configuration for production deployment
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes - Optimized for memory efficiency
workers = 1  # Single worker to prevent memory issues on free tier
worker_class = "sync"
worker_connections = 100  # Reduced for memory efficiency
timeout = 300  # Increased timeout for long-running scans
keepalive = 2

# Memory management - Optimized for low memory environments
max_requests = 100  # Restart workers frequently to prevent memory leaks
max_requests_jitter = 10
preload_app = True  # Critical for faster startup

# Timeout optimization for security scans
graceful_timeout = 120  # Allow time for scans to complete
worker_timeout = 300  # Extended timeout for advanced scans

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "ztionsec"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
worker_tmp_dir = "/dev/shm"  # Use memory for temporary files

def when_ready(server):
    server.log.info("ZtionSec server is ready. Listening on: %s", server.address)

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker aborted (pid: %s)", worker.pid)
