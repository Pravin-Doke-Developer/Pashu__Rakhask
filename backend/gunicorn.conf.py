import multiprocessing

# Timeout for silent workers (in seconds)
# Increased to 120 seconds to allow time for model loading
timeout = 120

# Number of worker processes
# Set to 1 to conserve memory on Render free tier
workers = 1

# Worker type
# Use sync worker for better memory management
worker_class = 'sync'

# Worker connections
worker_connections = 1000

# Max requests per worker before restart
# Helps prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Keepalive timeout
keepalive = 2

# Preload app (reduces memory overhead per worker)
preload_app = True

# Access log format
accesslog = '-'

# Log level
loglevel = 'info'

# Bind address (Render sets PORT env var)
bind = '0.0.0.0:' + str(__import__('os').environ.get('PORT', 5000))
