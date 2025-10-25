from http import HTTPStatus
from apps.aso.models import Order
from apps.users.serializers import UserOrderSummarySerializer
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys


class GetUserProfileSummaryQuery:

    @staticmethod
    def query(user):
        cache_key = CacheKeys.format(CacheKeys.USER_PROFILE, user_id=user.id)

        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            print("from cache")
            return BaseResultWithData(
                data=cached_data["data"],
                status_code=HTTPStatus.OK,
                message="User profile fetched successfully"
            )
        try:
            orders = Order.objects.filter(user=user, is_deleted = False).order_by('-created_at')

            data = {
                "first_name": user.first_name or "Not set",
                "last_name": user.last_name or "Not set",
                "email": user.email,
                "phone": user.phone or "Not set",
                "total_orders": orders.count(),
                "recent_orders": orders[:5]
            }
            
            serializer = UserOrderSummarySerializer(data)
            
            GlobalCache.set(cache_key, {"data": serializer.data})
            
            return BaseResultWithData(
                data=serializer.data,
                status_code=HTTPStatus.OK,
                message="User profile summary fetched successfully"
            )

        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to retrieve profile summary: {str(e)}"
            )
