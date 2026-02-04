from apps.aso.models import Notification
from utils.base_result import BaseResult
from http import HTTPStatus


class MarkAllNotificationsReadCommand:
    
    @staticmethod
    def Execute(user):
        """Mark all unread notifications as read for the user"""
        updated_count = Notification.objects.filter(
            user=user, 
            is_read=False
        ).update(is_read=True)
        
        return BaseResult(
            status_code=HTTPStatus.OK,
            message=f'{updated_count} notification(s) marked as read'
        )

