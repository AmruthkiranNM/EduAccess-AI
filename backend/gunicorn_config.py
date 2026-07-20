import multiprocessing
import os

# Gunicorn configuration for AWS EC2 Deployment

# The bind socket
bind = "0.0.0.0:5000"

# Number of worker processes (Recommended: 2-4 x $(NUM_CORES))
workers = multiprocessing.cpu_count() * 2 + 1

# The type of workers to use (sync by default, gevent/eventlet for high I/O)
worker_class = "sync"

# Maximum number of pending connections
backlog = 2048

# Maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Timeout for graceful workers restart
timeout = 30

# Logging configurations
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"

# Ensure security by running as a non-root user (if specified in OS)
# user = "www-data"
# group = "www-data"
