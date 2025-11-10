from celery import shared_task
from utils.decorators import checkBackgroundFeatureFlag



@checkBackgroundFeatureFlag()
@shared_task
def add(x, y):
    print(f"Adding {x} + {y}")
    return x + y


