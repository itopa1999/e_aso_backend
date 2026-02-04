from django.shortcuts import get_object_or_404
from apps.aso.models import Notification
from utils.base_result import BaseResult
from http import HTTPStatus


class DeleteNotificationCommand:
    
    @staticmethod
    def Execute(user, notification_id):
        notification = get_object_or_404(Notification, id=notification_id, user=user)
        notification.delete()
        
        return BaseResult(
            status_code=HTTPStatus.NO_CONTENT,
            message='Notification deleted'
        )

