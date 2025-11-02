from http import HTTPStatus
from apps.aso.models import Cart
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger


class UpdateCartStateCommand:
    @staticmethod
    def execute(user, state):
        op = OperationLogger("Update cart state", user=user.id if user else "Anonymous")
        op.start()
        cart, _ = Cart.objects.get_or_create(user=user, is_deleted=False)
        cart.state = state
        cart.save()
        
        op.success(f"Updated cart {cart.id} state to {state}")

        return BaseResultWithData(
            data={"cart_id": cart.id, "state": cart.state},
            status_code=HTTPStatus.OK,
            message="Cart state updated successfully"
        )
