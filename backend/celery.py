# celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")

app = Celery("your_project")

# Use Redis as the broker and result backend
app.conf.broker_url = "redis://127.0.0.1:6780/0"
app.conf.result_backend = "redis://127.0.0.1:6780/0"

# Optional: timezone
app.conf.timezone = "UTC"

app.autodiscover_tasks()
