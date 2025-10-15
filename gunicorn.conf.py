# Gunicorn configuration for production deployment
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes - Optimized for cold start prevention
workers = min(2, multiprocessing.cpu_count())  # Limit workers for memory
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5  # Increased keepalive for better connection reuse

# Memory management - Optimized for faster startup
max_requests = 1500  # Increased for better performance
max_requests_jitter = 100
preload_app = True  # Critical for faster startup

# Cold start optimization
graceful_timeout = 60  # Faster graceful shutdown
worker_timeout = 120  # Worker timeout

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
