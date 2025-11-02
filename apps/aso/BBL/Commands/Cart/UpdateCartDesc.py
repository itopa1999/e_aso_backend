from http import HTTPStatus
from apps.aso.models import CartItem
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger


class UpdateCartDescCommand:
    @staticmethod
    def execute(user, serializer):
        op = OperationLogger("Update cart description", user=user.id if user else "Anonymous")
        op.start()
        if not serializer.is_valid():
            op.fail("Invalid serializer data")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message=serializer.errors
            )
        
        item_id = serializer.validated_data["item_id"]
        desc = serializer.validated_data["desc"]
        
        try:
            item = CartItem.objects.get(
                id=item_id,
                cart__user=user,
                is_deleted=False
            )

            item.desc = desc
            item.save()

            op.success(f"Updated description for item {item.id}")
            return BaseResultWithData(
                data={"item_id": item.id, "desc": item.desc},
                status_code=HTTPStatus.OK,
                message="Cart item description updated successfully"
            )

        except CartItem.DoesNotExist:
            op.fail(f"Cart item {item_id} not found")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.NOT_FOUND,
                message="Cart item not found"
            )
