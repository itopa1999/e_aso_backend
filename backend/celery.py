import os
from celery import Celery

# Set the default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Create Celery app
app = Celery('aso-backend')

# Load settings from Django’s settings.py using a CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in installed apps
app.autodiscover_tasks()

# app.conf.imports = (
#     'utils.Tasks.tasks',
#     'utils.Tasks.ApplyBlackFridayDiscount',
#     'utils.Tasks.ResetBlackFridayDiscount',
#     'utils.Tasks.SetLimitedProduct',
#     'utils.Tasks.UnsetLimitedProduct',
#     'utils.Tasks.Emails.EmailForBlackFriday',
#     'utils.Tasks.Emails.EmailForLimitedProducts',
#     'utils.Tasks.Emails.EmailForFreeShipping',
#     'utils.Tasks.Emails.EmailForRefferralDiscount',
#     'utils.Tasks.Emails.EmailForProductAds',
#     ''
# )

# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
