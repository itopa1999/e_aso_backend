from http import HTTPStatus
from apps.aso.models import CartItem
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger


class UpdateCartQuantityCommand:
    @staticmethod
    def execute(user, serializer):
        op = OperationLogger("Update cart quantity", user=user.id if user else "Anonymous")
        op.start()
        if not serializer.is_valid():
            op.fail("Invalid serializer data")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message=serializer.errors
            )
        
        item_id = serializer.validated_data["item_id"]
        quantity = serializer.validated_data["quantity"]
        
        try:
            item = CartItem.objects.get(
                id=item_id,
                cart__user=user,
                is_deleted=False
            )

            item.quantity = quantity
            item.save()

            op.success(f"Updated item {item_id} to quantity {quantity}")
            return BaseResultWithData(
                data={"item_id": item.id, "quantity": item.quantity},
                status_code=HTTPStatus.OK,
                message="Cart item quantity updated successfully"
            )

        except CartItem.DoesNotExist:
            op.fail(f"Cart item {item_id} not found")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.NOT_FOUND,
                message="Cart item not found"
            )
        except Exception as e:
            op.fail(str(e))
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to update cart item quantity: {str(e)}"
            )
