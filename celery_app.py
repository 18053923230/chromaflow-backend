from celery import Celery
from dotenv import load_dotenv
import os

# Load environment variables. Crucial for Render as well.
load_dotenv()

# Get Redis URL from environment variables
# Default to localhost if not set (for local dev without .env)
redis_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend_url = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Initialize Celery
# The first argument is the name of the current module.
# The 'broker' argument specifies the URL of the message broker (Redis).
# The 'backend' argument specifies the URL of the result backend (Redis).
# 'include' tells Celery where to find your task modules.
celery_instance = Celery(
    'chromaflow_tasks', # A name for your celery tasks module
    broker=redis_url,
    backend=result_backend_url,
    include=['app.tasks.image_processing_tasks'] # Path to your tasks file
)

# Optional configuration
celery_instance.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ensure Celery accepts JSON content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # It's good practice to set a task time limit to prevent runaway tasks
    # task_time_limit=300,  # 5 minutes, adjust as needed
    # task_soft_time_limit=240, # 4 minutes
)

if __name__ == '__main__':
    # This is for running the worker directly (e.g., in a Docker container)
    # For local development, you typically run:
    # celery -A celery_app.celery_instance worker -l info
    celery_instance.start()