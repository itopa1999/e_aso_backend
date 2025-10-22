from http import HTTPStatus
from utils.base_result import BaseResultWithData
from apps.aso.models import Cart, WatchList
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys


class CartAndWatchlistCountQuery:
    @staticmethod
    def query(user):
        cache_key = CacheKeys.format(CacheKeys.USER_WATCHLISTCART, user_id=user.id)

        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            return BaseResultWithData(
                data=cached_data["data"],
                status_code=HTTPStatus.OK,
                message="Order details fetched successfully"
            )
            
        try:
            cart_count = 0
            try:
                cart = Cart.objects.get(user=user, is_deleted=False)
                cart_count = cart.items.count()
            except Cart.DoesNotExist:
                pass

            watchlist_count = WatchList.objects.filter(
                user=user, is_deleted=False
            ).count()
            
            GlobalCache.set(cache_key, {"data": {"item_count": cart_count, "watchlist_count": watchlist_count}})

            return BaseResultWithData(
                data={"item_count": cart_count, "watchlist_count": watchlist_count},
                status_code=HTTPStatus.OK,
                message="Cart and watchlist counts retrieved successfully."
            )

        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to fetch cart/watchlist counts: {str(e)}"
            )
