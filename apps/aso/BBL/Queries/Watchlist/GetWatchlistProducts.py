# apps/aso/queries/get_watchlist_products_query.py
from http import HTTPStatus
from apps.aso.models import Product
from apps.aso.serializers import WatchlistProductSerializer
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys


class GetWatchlistProductsQuery:
    @staticmethod
    def query(user, request=None):
        cache_key = CacheKeys.format(CacheKeys.USER_WATCHLIST, user_id=user.id)

        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            return BaseResultWithData(
                data=cached_data["data"],
                status_code=HTTPStatus.OK,
                message="Watchlist fetched successfully"
            )
            
            
        queryset = Product.objects.filter(
            watchlist_product__user=user,
            is_deleted=False
        )

        serializer = WatchlistProductSerializer(queryset, many=True, context={"request": request})
        
        GlobalCache.set(cache_key, {"data": serializer.data})
        
        return BaseResultWithData(
            data=serializer.data,
            status_code=HTTPStatus.OK,
            message="Watchlist fetched successfully"
        )
