"""
Celery beat scheduled tasks for daily operations
"""
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.aso.models import FeatureFlag

from utils.Tasks.Emails.EmailRemiderForAbadonnedCart import send_abandoned_cart_reminders
from utils.decorators import checkBackgroundFeatureFlag

User = get_user_model()


# ============================================================================
# PURE LOGIC FUNCTIONS (No decorators, can be called directly or via Celery)
# ============================================================================

def _send_abandoned_cart_reminders_logic():
    """
    Pure logic for sending abandoned cart reminders.
    Can be called directly or via Celery task.
    """
    try:
        result = send_abandoned_cart_reminders()
        print(f"✅ {result}")
        return result
    except Exception as e:
        print(f"❌ Error in abandoned cart reminders: {e}")
        return f"Error: {str(e)}"


def _deactivate_expired_feature_flags_logic():
    """
    Pure logic for deactivating expired feature flags.
    Can be called directly or via Celery task.
    """
    try:
        now = timezone.now()
        
        # Find all active feature flags with expired end dates
        expired_flags = FeatureFlag.objects.filter(
            is_enabled=True,
            is_active=True,
            end_date__lte=now,
            is_deleted=False
        )
            
        count = 0
        for flag in expired_flags:
            flag.is_enabled = False
            flag.is_active = False
            flag.end_date = None
            flag.start_date = None
            flag.discount_percent = None
            flag.save(update_fields=['is_enabled', 'is_active', 'end_date', 'start_date', 'discount_percent'])
            count += 1
            print(f"✅ Deactivated expired feature flag: {flag.name}")
            
        result = f"✅ Deactivated {count} expired feature flag(s)."
        print(result)
        return result
    except Exception as e:
        print(f"❌ Error in deactivate expired feature flags: {e}")
        return f"Error: {str(e)}"


# ============================================================================
# CELERY BEAT SCHEDULED TASKS (For automated scheduling)
# ============================================================================
@checkBackgroundFeatureFlag()
@shared_task(bind=True)
def send_abandoned_cart_reminders_daily(self):
    """
    Daily task to send email reminders for abandoned carts.
    Runs automatically via Celery Beat schedule.
    """
    return _send_abandoned_cart_reminders_logic()

@checkBackgroundFeatureFlag()
@shared_task(bind=True)
def deactivate_expired_feature_flags(self):
    """
    Daily task to check and deactivate feature flags whose end_date has expired.
    Runs automatically via Celery Beat schedule.
    """
    return _deactivate_expired_feature_flags_logic()


# ============================================================================
# BACKGROUND TASK WRAPPERS (For manual triggering when workers are limited)
# ============================================================================

@checkBackgroundFeatureFlag()
@shared_task
def send_abandoned_cart_reminders_background():
    """
    Background task wrapper for abandoned cart reminders.
    Call this when you want to trigger the task manually as a background job.
    
    Usage:
        from utils.Tasks.scheduled_tasks import send_abandoned_cart_reminders_background
        send_abandoned_cart_reminders_background.delay()
    """
    return _send_abandoned_cart_reminders_logic()


@checkBackgroundFeatureFlag()
@shared_task
def deactivate_expired_feature_flags_background():
    """
    Background task wrapper for feature flag deactivation.
    Call this when you want to trigger the task manually as a background job.
    
    Usage:
        from utils.Tasks.scheduled_tasks import deactivate_expired_feature_flags_background
        deactivate_expired_feature_flags_background.delay()
    """
    return _deactivate_expired_feature_flags_logic()

