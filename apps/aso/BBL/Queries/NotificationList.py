from rest_framework.pagination import PageNumberPagination
from apps.aso.models import Notification
from apps.aso.serializers import NotificationSerializer
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys
from http import HTTPStatus


class NotificationListQuery:
    
    @staticmethod
    def Execute(user, request):
        # Create cache key for this user's notifications
        cache_key = CacheKeys.format(CacheKeys.USER_NOTIFICATIONS, user_id=user.id)
        
        # Try to get from cache
        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            return BaseResultWithData(
                data=cached_data,
                status_code=HTTPStatus.OK,
                message='Notifications retrieved successfully (cached)'
            )
        
        # If not in cache, fetch from database
        notifications = Notification.objects.filter(user=user).order_by('-created_at')
        
        paginator = PageNumberPagination()
        paginator.page_size = 100
        
        paginated_notifs = paginator.paginate_queryset(notifications, request)
        serializer = NotificationSerializer(paginated_notifs, many=True)
        
        # Cache the paginated data
        response_data = {
            'results': serializer.data,
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link()
        }
        GlobalCache.set(cache_key, response_data)
        
        return BaseResultWithData(
            data=response_data,
            status_code=HTTPStatus.OK,
            message='Notifications retrieved successfully'
        )
