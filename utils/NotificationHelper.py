"""
Notification helper to create and manage notification instances.
Provides utility functions for creating notifications for various events.
"""
from apps.aso.models import Notification
from utils.enum import NotificationType


class NotificationHelper:
    """Helper class for creating and managing notifications."""
    
    @staticmethod
    def create_order_update_notification(user, order, status, description=None):
        """
        Create a notification when an order status is updated.
        
        Args:
            user: User object
            order: Order object
            status: New order status (e.g., 'placed', 'processing', 'shipped')
            description: Optional detailed description
            
        Returns:
            Notification instance
        """
        title = f"Order {order.order_number} Updated"
        
        # Build message based on status
        status_messages = {
            'placed': 'Your order has been placed successfully! 🎉',
            'processing': 'Your order is being processed by our team. 📦',
            'shipped': 'Your order has been shipped! 🚚',
            'in_transit': 'Your order is on its way to you! 🚚',
            'delivered': 'Your order has been delivered! ✅',
            'cancelled': 'Your order has been cancelled.',
        }
        
        message = status_messages.get(
            status.lower(), 
            f'Your order status has been updated to: {status}'
        )
        
        if description:
            message += f"\n{description}"
        
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            type=NotificationType.UPDATES.value,
            action_url=f"/orders/{order.id}/"
        )
        
        return notification
    
    @staticmethod
    def create_system_notification(user, title, message, action_url=None):
        """
        Create a generic system notification.
        
        Args:
            user: User object
            title: Notification title
            message: Notification message
            action_url: Optional URL for the notification action
            
        Returns:
            Notification instance
        """
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            type=NotificationType.SYSTEM.value,
            action_url=action_url
        )
        
        return notification
    
    @staticmethod
    def create_promo_notification(user, title, message, action_url=None):
        """
        Create a promotional notification.
        
        Args:
            user: User object
            title: Notification title
            message: Notification message
            action_url: Optional URL for the promotion
            
        Returns:
            Notification instance
        """
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            type=NotificationType.PROMOTION.value,
            action_url=action_url
        )
        
        return notification
