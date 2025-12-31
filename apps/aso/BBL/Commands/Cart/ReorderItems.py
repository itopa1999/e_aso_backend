from apps.aso.models import Order, Cart, CartItem
from apps.aso.serializers import AddToCartCountResponseSerializer
from http import HTTPStatus
from django.db import transaction
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger

class ReorderItemsCommand:

    @staticmethod
    def execute(user, order_id):
        op = OperationLogger("Reorder items", user=user.id if user else "Anonymous")
        op.start()
        
        if not order_id:
            op.fail("Missing order_id")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message="order_id is required"
            )
        try:
            order = Order.objects.get(id=order_id, user=user, is_deleted = False)
        except Order.DoesNotExist:
            op.fail(f"Order {order_id} not found")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.NOT_FOUND,
                message="Order not found"
            )

        with transaction.atomic():
            cart, _ = Cart.objects.get_or_create(user=user, is_deleted = False)
            items_added = 0

            for item in order.items.all():
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=item.product,
                    defaults={"quantity": item.quantity}, is_deleted = False
                )
                if created:
                    items_added += 1

        serializer = AddToCartCountResponseSerializer({"items_added": items_added})
        
        op.success(f"Reordered {items_added} items from order {order_id}")
        return BaseResultWithData(
            data=serializer.data,
            status_code=HTTPStatus.OK,
            message="Items reordered successfully"
        )
