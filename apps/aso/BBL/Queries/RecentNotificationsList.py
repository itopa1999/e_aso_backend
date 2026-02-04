from apps.aso.models import Notification
from apps.aso.serializers import NotificationSerializer
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys
from http import HTTPStatus


class RecentNotificationsListQuery:
    
    @staticmethod
    def Execute(user):
        # Create cache key for this user's recent notifications
        cache_key = CacheKeys.format(CacheKeys.USER_NOTIFICATIONS_RECENT, user_id=user.id)
        
        # Try to get from cache
        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            return BaseResultWithData(
                data=cached_data,
                status_code=HTTPStatus.OK,
                message='Recent notifications retrieved successfully (cached)'
            )
        
        # If not in cache, fetch from database
        notifications = Notification.objects.filter(user=user).order_by('-created_at')[:5]
        
        serializer = NotificationSerializer(notifications, many=True)
        
        # Cache the data
        response_data = serializer.data
        GlobalCache.set(cache_key, response_data)
        
        return BaseResultWithData(
            data=response_data,
            status_code=HTTPStatus.OK,
            message='Recent notifications retrieved successfully'
        )
