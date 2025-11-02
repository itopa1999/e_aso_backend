from http import HTTPStatus
from apps.aso.models import Order
from apps.aso.serializers import OrderSerializer
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys

class UserOrderListQuery:

    @staticmethod
    def query(request):
        user = request.user
        cache_key = CacheKeys.format(CacheKeys.USER_ORDERS, user_id=user.id)

        # ✅ Try cache first
        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            return BaseResultWithData(
                data=cached_data["data"],
                status_code=HTTPStatus.OK,
                message="User orders fetched successfully"
            )
            
        orders = Order.objects.filter(user=user, is_deleted = False).prefetch_related('items', 'tracking_events').order_by('-created_at')
        serializer = OrderSerializer(orders, many=True, context={'request': request})
        
        GlobalCache.set(cache_key, {"data": serializer.data})
        
        return BaseResultWithData(
            data=serializer.data,
            status_code=HTTPStatus.OK,
            message="User orders fetched successfully"
        )
