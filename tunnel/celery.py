import os
from celery import Celery
import logging

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunnel.settings')

app = Celery('tunnel')

app.conf.update(
    result_backend='django-db',
    result_expires=3600,
    task_track_started=True,
    task_acks_on_failure_or_timeout=True,
    worker_concurrency=8,
    worker_pool='prefork',
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    broker_heartbeat=30,
)
# Using a string here means the worker does not have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

logger = logging.getLogger('core')
logger.setLevel(logging.INFO)  # Adjust level as needed

# Setup a file handler for logging Celery results
handler = logging.FileHandler('celery_results.log')
handler.setLevel(logging.INFO)  # Log level for results

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)