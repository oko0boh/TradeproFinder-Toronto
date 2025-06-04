"""
Gunicorn configuration for Tradepro Finder Toronto.
"""

import multiprocessing
import os

# Server socket
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
# proc_name = 'tradepro-finder'  # Commented out to prevent issues on Render
# pythonpath = '/var/www/tradepro-finder' # Commented out, Render handles pythonpath

# Logging
accesslog = 'logs/access.log'  # Use relative path in the app directory
errorlog = 'logs/error.log'    # Use relative path in the app directory
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# SSL
# keyfile = '/etc/ssl/private/tradepro-finder.key' # Commented out, Render handles SSL
# certfile = '/etc/ssl/certs/tradepro-finder.crt'  # Commented out, Render handles SSL

# Server mechanics
daemon = False
pidfile = '/var/run/tradepro-finder.pid'
umask = 0
user = 'www-data'
group = 'www-data'
tmp_upload_dir = None

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Server hooks
def on_starting(server):
    """Log when the server starts."""
    server.log.info('Starting Tradepro Finder Toronto')

def on_reload(server):
    """Log when the server reloads."""
    server.log.info('Reloading Tradepro Finder Toronto')

def on_exit(server):
    """Log when the server exits."""
    server.log.info('Stopping Tradepro Finder Toronto')
