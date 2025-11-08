from apps.aso.models import Order
from apps.aso.serializers import OrderDetailSerializer
from http import HTTPStatus
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys

class OrderDetailQuery:

    @staticmethod
    def query(request, order_id):
        user = request.user
        cache_key = CacheKeys.format(CacheKeys.ORDER_DETAIL, user_id=user.id, order_id=order_id)

        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            return BaseResultWithData(
                data=cached_data["data"],
                status_code=HTTPStatus.OK,
                message="Order details fetched successfully"
            )
            
        
        try:
            order = Order.objects.get(user=user, id=order_id, is_deleted = False)
            serializer = OrderDetailSerializer(order, context={'request': request})
            
            GlobalCache.set(cache_key, {"data": serializer.data})
            
            return BaseResultWithData(
                data=serializer.data,
                status_code=HTTPStatus.OK,
                message="Order details fetched successfully"
            )
        except Order.DoesNotExist:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.NOT_FOUND,
                message="Order not found"
            )
