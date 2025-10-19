# apps/aso/commands/move_all_to_cart_command.py
from http import HTTPStatus
from apps.aso.models import WatchList, Cart, CartItem
from utils.base_result import BaseResultWithData


class MoveAllToCartCommand:
    @staticmethod
    def execute(user):
        try:
            watchlist_items = WatchList.objects.filter(user=user, is_deleted=False)
            if not watchlist_items.exists():
                return BaseResultWithData(
                    data={"items_added": 0},
                    status_code=HTTPStatus.OK,
                    message="No items in watchlist to move"
                )

            cart, _ = Cart.objects.get_or_create(user=user, is_deleted=False)
            items_added = 0

            for item in watchlist_items:
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=item.product,
                    defaults={'quantity': 1},
                    is_deleted=False
                )
                if created:
                    items_added += 1

            return BaseResultWithData(
                data={"items_added": items_added},
                status_code=HTTPStatus.OK,
                message=f"{items_added} items moved to cart"
            )

        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to move watchlist to cart: {str(e)}"
            )
