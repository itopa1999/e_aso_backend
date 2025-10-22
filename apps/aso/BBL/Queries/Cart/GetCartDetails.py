from http import HTTPStatus
from apps.aso.models import Cart
from apps.aso.serializers import CartDetailSerializer
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys


class GetCartDetailQuery:
    @staticmethod
    def query(user):
        cache_key = CacheKeys.format(CacheKeys.USER_CART, user_id=user.id)

        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            return BaseResultWithData(
                data=cached_data["data"],
                status_code=HTTPStatus.OK,
                message="Watchlist fetched successfully"
            )
            
        try:
            cart, created = Cart.objects.get_or_create(user=user, is_deleted=False)

            serializer = CartDetailSerializer(cart)
            
            GlobalCache.set(cache_key, {"data": serializer.data})
            
            return BaseResultWithData(
                data=serializer.data,
                status_code=HTTPStatus.OK,
                message="Cart detail retrieved successfully"
            )

        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to fetch cart details: {str(e)}"
            )
