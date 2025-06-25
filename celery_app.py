from celery import Celery
from dotenv import load_dotenv
import os



load_dotenv()

redis_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend_url = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')



celery_instance = Celery(
    'chromaflow_tasks',
    broker=redis_url,
    backend=result_backend_url,
    # include=['app.tasks.image_processing_tasks'] # TEMPORARILY COMMENTED OUT or set to include=[]
    include=['app.tasks.image_processing_tasks'] # 恢复这一行
)

celery_instance.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
