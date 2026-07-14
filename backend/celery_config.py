import os
import sys

# Ensure backend directory is in Python path (needed for Celery worker forks)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from celery import Celery
from celery.schedules import crontab

# Create Celery app with Redis as broker and backend
celery_app = Celery(
    'trekking_app',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# Celery configuration
celery_app.conf.update(
    timezone='Asia/Kolkata',
    enable_utc=False,
    # Auto-discover tasks from tasks.py
    imports=['tasks']
)

# Beat schedule — scheduled tasks
celery_app.conf.beat_schedule = {
    'daily-reminder': {
        'task': 'tasks.daily_reminder',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9 AM
    },
    'monthly-report': {
        'task': 'tasks.monthly_report',
        'schedule': crontab(day_of_month=1, hour=8, minute=0),  # 1st of every month at 8 AM
    }
}
