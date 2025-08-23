# gunicorn_config.py

# Use the eventlet worker class for WebSocket support
worker_class = 'eventlet'

# The number of worker processes
workers = 1

# The socket to bind to
bind = '0.0.0.0:8080'

# Set a timeout for workers
timeout = 120

# Log to stdout
accesslog = '-'
errorlog = '-'
