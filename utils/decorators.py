from functools import wraps
from utils.feature_flags import is_feature_enabled
from utils.enum import FeatureNames

def checkBackgroundFeatureFlag(feature_name=FeatureNames.BACKGROUND_TASKS.value):
    """
    Run function as a Celery task only if BACKGROUND_TASKS feature is enabled.
    Otherwise, execute synchronously.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            flag, enabled = is_feature_enabled(feature_name)

            if enabled:
                if hasattr(func, "delay"):
                    print(f"🚀 Running {func.__name__} as Celery task...")
                    return func.delay(*args, **kwargs)
                else:
                    print(f"⚠️ {func.__name__} has no delay() — maybe decorator order?")
            else:
                print(f"🧩 Background feature OFF → running {func.__name__} synchronously")

            return func(*args, **kwargs)

        return wrapper
    return decorator
