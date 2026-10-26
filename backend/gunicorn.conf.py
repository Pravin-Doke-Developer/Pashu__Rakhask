import multiprocessing

# Timeout for silent workers (in seconds)
# Increased to 180 seconds to allow time for model loading and prediction on slow Render free tier
timeout = 180

# Number of worker processes
# Set to 1 to conserve memory on Render free tier
workers = 1

# Worker type
# Use sync worker for better memory management
worker_class = 'sync'

# Worker connections
worker_connections = 1000

# Max requests per worker before restart
# Reduced to prevent memory accumulation
max_requests = 100
max_requests_jitter = 10

# Keepalive timeout
keepalive = 2

# Graceful timeout for worker shutdown
graceful_timeout = 30

# Preload app (reduces memory overhead per worker)
preload_app = True

# Access log format
accesslog = '-'

# Log level
loglevel = 'info'

# Bind address (Render sets PORT env var)
bind = '0.0.0.0:' + str(__import__('os').environ.get('PORT', 5000))
