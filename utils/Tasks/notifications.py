"""
Celery tasks for handling notifications.
Processes notification creation asynchronously in background.
"""
from celery import shared_task
from celery.utils.log import get_task_logger
from utils.decorators import checkBackgroundFeatureFlag
from utils.NotificationHelper import NotificationHelper
from django.contrib.auth import get_user_model

logger = get_task_logger(__name__)
User = get_user_model()


@checkBackgroundFeatureFlag()
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def create_order_update_notification(self, user_id, order_id, status, description=None):
    """
    Create a notification for order status updates asynchronously.
    
    Args:
        user_id: ID of the user
        order_id: ID of the order
        status: New order status
        description: Optional description
        
    Returns:
        Notification ID on success
    """
    try:
        from apps.aso.models import Order
        
        user = User.objects.get(id=user_id)
        order = Order.objects.get(id=order_id)
        
        notification = NotificationHelper.create_order_update_notification(
            user=user,
            order=order,
            status=status,
            description=description
        )
        
        logger.info(f"✅ Created notification {notification.id} for user {user_id} - Order {order_id} ({status})")
        return notification.id
        
    except User.DoesNotExist:
        logger.error(f"❌ User {user_id} not found")
        return None
    except Exception as e:
        logger.error(f"❌ Error creating order notification: {e}")
        # Retry the task with exponential backoff
        raise self.retry(exc=e)


@checkBackgroundFeatureFlag()
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def create_system_notification(self, user_id, title, message, action_url=None):
    """
    Create a system notification asynchronously.
    
    Args:
        user_id: ID of the user
        title: Notification title
        message: Notification message
        action_url: Optional action URL
        
    Returns:
        Notification ID on success
    """
    try:
        user = User.objects.get(id=user_id)
        
        notification = NotificationHelper.create_system_notification(
            user=user,
            title=title,
            message=message,
            action_url=action_url
        )
        
        logger.info(f"✅ Created system notification {notification.id} for user {user_id}")
        return notification.id
        
    except User.DoesNotExist:
        logger.error(f"❌ User {user_id} not found")
        return None
    except Exception as e:
        logger.error(f"❌ Error creating system notification: {e}")
        raise self.retry(exc=e)


@checkBackgroundFeatureFlag()
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def create_promo_notification(self, user_id, title, message, action_url=None):
    """
    Create a promotional notification asynchronously.
    
    Args:
        user_id: ID of the user
        title: Notification title
        message: Notification message
        action_url: Optional promotion URL
        
    Returns:
        Notification ID on success
    """
    try:
        user = User.objects.get(id=user_id)
        
        notification = NotificationHelper.create_promo_notification(
            user=user,
            title=title,
            message=message,
            action_url=action_url
        )
        
        logger.info(f"✅ Created promo notification {notification.id} for user {user_id}")
        return notification.id
        
    except User.DoesNotExist:
        logger.error(f"❌ User {user_id} not found")
        return None
    except Exception as e:
        logger.error(f"❌ Error creating promo notification: {e}")
        raise self.retry(exc=e)
