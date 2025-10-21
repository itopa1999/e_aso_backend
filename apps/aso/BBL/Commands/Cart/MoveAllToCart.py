from http import HTTPStatus
from apps.aso.models import WatchList, Cart, CartItem
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger


class MoveAllToCartCommand:
    @staticmethod
    def execute(user):
        op = OperationLogger(
            "MoveAllToCartCommand",
            user=user.id if user else "Anonymous"
        )
        op.start()
        try:
            watchlist_items = WatchList.objects.filter(user=user, is_deleted=False)
            if not watchlist_items.exists():
                op.fail("No items in watchlist to move")
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
                    
            op.success(f"{items_added} items moved to cart")
            return BaseResultWithData(
                data={"items_added": items_added},
                status_code=HTTPStatus.OK,
                message=f"{items_added} items moved to cart"
            )

        except Exception as e:
            op.fail("Failed to move watchlist to cart", e)
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to move watchlist to cart: {str(e)}"
            )
