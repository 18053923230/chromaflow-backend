from celery import Celery
from dotenv import load_dotenv
import os

print(">>>> celery_app.py: SCRIPT EXECUTION STARTED <<<<") # 新增

load_dotenv()

redis_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend_url = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
print(f">>>> celery_app.py: Redis URL configured: {redis_url}") # 新增

print(">>>> celery_app.py: About to initialize Celery app instance (WITHOUT include for now)... <<<<") # 新增
celery_instance = Celery(
    'chromaflow_tasks',
    broker=redis_url,
    backend=result_backend_url,
    # include=['app.tasks.image_processing_tasks'] # TEMPORARILY COMMENTED OUT or set to include=[]
    include=[] # 显式置空
)
print(">>>> celery_app.py: Celery app instance INITIALIZED. <<<<") # 新增

print(">>>> celery_app.py: About to update Celery config... <<<<") # 新增
celery_instance.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
print(">>>> celery_app.py: Celery config UPDATED. <<<<") # 新增
print(">>>> celery_app.py: SCRIPT EXECUTION FINISHED <<<<") # 新增