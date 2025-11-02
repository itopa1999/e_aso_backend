from http import HTTPStatus
from apps.aso.models import Cart
from apps.aso.serializers import CartDetailSerializer
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys


class GetCartDetailQuery:
    @staticmethod
    def query(request):
        user = request.user
        cache_key = CacheKeys.format(CacheKeys.USER_CART, user_id=user.id)

        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            return BaseResultWithData(
                data=cached_data["data"],
                status_code=HTTPStatus.OK,
                message="Watchlist fetched successfully"
            )
            
        cart, created = Cart.objects.get_or_create(user=user, is_deleted=False)

        serializer = CartDetailSerializer(cart, context={'request': request})
        
        GlobalCache.set(cache_key, {"data": serializer.data})
        
        return BaseResultWithData(
            data=serializer.data,
            status_code=HTTPStatus.OK,
            message="Cart detail retrieved successfully"
        )


