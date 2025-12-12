from http import HTTPStatus
from apps.users.serializers import TelegramNotificationSerializer
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger


class ManageTelegramNotificationCommand:

    @staticmethod
    def Execute(user, action_data):
        """
        Manage Telegram notifications for a user.
        
        Args:
            user: The authenticated user
            action_data: Dictionary with 'action' and optional 'telegram_user_id'
        
        Returns:
            BaseResult with status and message
        """
        op = OperationLogger(
            "ManageTelegramNotificationCommand",
            user=user.id if user else "Anonymous"
        )
        op.start()
        
        serializer = TelegramNotificationSerializer(data=action_data)
        
        if not serializer.is_valid():
            op.fail(f"Validation failed: {serializer.errors}")
            return BaseResultWithData(
                status_code=HTTPStatus.BAD_REQUEST,
                message="Invalid data",
                data=serializer.errors
            )
        
        action = serializer.validated_data.get('action')
        telegram_user_id = serializer.validated_data.get('telegram_user_id')
        
        if action == 'activate':
            if not telegram_user_id:
                op.fail("telegram_user_id is required for activation")
                return BaseResultWithData(
                    status_code=HTTPStatus.BAD_REQUEST,
                    message="telegram_user_id is required for activation",
                    data=None
                )
            
            # Update user with telegram info and enable notifications
            user.telegram_user_id = telegram_user_id
            user.telegram_user_chat_id = str(telegram_user_id)
            user.telegram_notifications_enabled = True
            user.save(update_fields=['telegram_user_id', 'telegram_user_chat_id', 'telegram_notifications_enabled'])
            
            op.success(f"Telegram notifications activated for user {user.id}")
            return BaseResultWithData(
                status_code=HTTPStatus.OK,
                message="Telegram notifications activated successfully",
                data={
                    'telegram_user_id': user.telegram_user_id,
                    'telegram_user_chat_id': user.telegram_user_chat_id,
                    'notifications_enabled': user.telegram_notifications_enabled
                }
            )
        
        elif action == 'deactivate':
            # Disable notifications
            user.telegram_notifications_enabled = False
            user.save(update_fields=['telegram_notifications_enabled'])
            
            op.success(f"Telegram notifications deactivated for user {user.id}")
            return BaseResultWithData(
                status_code=HTTPStatus.OK,
                message="Telegram notifications deactivated successfully",
                data={
                    'notifications_enabled': user.telegram_notifications_enabled
                }
            )
        
        else:
            op.fail(f"Invalid action: {action}")
            return BaseResultWithData(
                status_code=HTTPStatus.BAD_REQUEST,
                message='Invalid action. Use "activate" or "deactivate"',
                data=None
            )
