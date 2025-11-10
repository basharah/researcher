"""
Celery Application Configuration
Task queue for async document processing
"""
from celery import Celery
from config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "document_processing",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3000,  # 50 minutes soft limit
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks
    result_expires=86400,  # Keep results for 24 hours
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,
)

# Task routes
celery_app.conf.task_routes = {
    'tasks.process_document_task': {'queue': 'document_processing'},
    'tasks.process_batch_task': {'queue': 'batch_processing'},
    'tasks.extract_doi_task': {'queue': 'metadata_extraction'},
    'tasks.apply_ocr_task': {'queue': 'ocr_processing'},
}

logger.info("Celery app configured successfully")
