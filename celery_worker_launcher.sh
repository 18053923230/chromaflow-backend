#!/bin/bash
# This script will be used as the start command for the Celery worker on Render.
# It ensures that the Celery app instance is correctly referenced.

# The -A option specifies the Celery application instance.
# 'celery_app.celery_instance' means:
#   - 'celery_app' is the Python module (celery_app.py)
#   - 'celery_instance' is the Celery application object within that module.
# The 'worker' command starts a worker process.
# -l info sets the logging level to info.
# -P solo is a simple prefork pool, good for CPU-bound tasks if you have 1 worker per CPU core.
# For Render's free tier, 'solo' is fine. For paid plans, you might use 'prefork' (default) or 'eventlet'/'gevent' for I/O bound.
# We use 'solo' to be safe for resource limits on free tier initially.
celery -A celery_app.celery_instance worker -l info -P solo