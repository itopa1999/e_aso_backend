from http import HTTPStatus
from apps.aso.models import Cart
from utils.base_result import BaseResultWithData


class UpdateCartStateCommand:
    @staticmethod
    def execute(user, state):
        try:
            cart, _ = Cart.objects.get_or_create(user=user, is_deleted=False)
            cart.state = state
            cart.save()

            return BaseResultWithData(
                data={"cart_id": cart.id, "state": cart.state},
                status_code=HTTPStatus.OK,
                message="Cart state updated successfully"
            )

        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to update cart state: {str(e)}"
            )
