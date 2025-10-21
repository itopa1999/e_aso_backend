from http import HTTPStatus
from apps.aso.models import CartItem
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger


class DeleteAllCartItemsCommand:
    @staticmethod
    def execute(user):
        op = OperationLogger(
            "Delete all cart items",
            user=user.id if user else "Anonymous",
            product_id="None"
        )
        op.start()
        
        deleted_count = CartItem.objects.filter(cart__user=user, is_deleted=False).delete()
        if deleted_count == 0:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message="Already empty"
            )
        return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.OK,
                message="All cart items removed successfully"
            )