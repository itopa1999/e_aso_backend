
from http import HTTPStatus
from apps.aso.models import Order
from apps.aso.serializers import OrderTrackingDetailsSerializer
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys


class TrackingDetailsQuery:
    @staticmethod
    def query(user, order_id):
        cache_key = CacheKeys.format(CacheKeys.USER_ORDER_TRACKING, user_id=user.id, order_id=order_id)
        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            return BaseResultWithData(
                status_code=HTTPStatus.OK,
                message="Tracking details fetched successfully",
                data=cached_data["data"]
            )
            
        try:
            order = Order.objects.get(user=user, id=order_id, is_deleted=False)
        except Order.DoesNotExist:
            return BaseResultWithData(
                status_code=HTTPStatus.BAD_REQUEST,
                message="Order not found",
                data=None
            )
        serializer = OrderTrackingDetailsSerializer(order)
        GlobalCache.set(cache_key, {"data": serializer.data})
        return BaseResultWithData(
            status_code=HTTPStatus.OK,
            message="Tracking details fetched successfully",
            data=serializer.data
        )