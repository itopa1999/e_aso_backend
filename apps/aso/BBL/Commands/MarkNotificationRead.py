from django.shortcuts import get_object_or_404
from apps.aso.models import Notification
from apps.aso.serializers import NotificationSerializer
from utils.base_result import BaseResultWithData
from http import HTTPStatus


class MarkNotificationReadCommand:
    
    @staticmethod
    def Execute(user, notification_id):
        notification = get_object_or_404(Notification, id=notification_id, user=user)
        
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        
        serializer = NotificationSerializer(notification)
        
        return BaseResultWithData(
            data=serializer.data,
            status_code=HTTPStatus.OK,
            message='Notification marked as read'
        )

