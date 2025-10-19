from http import HTTPStatus
from apps.aso.models import CartItem
from utils.base_result import BaseResultWithData


class UpdateCartDescCommand:
    @staticmethod
    def execute(user, serializer):
        if not serializer.is_valid():
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

            return BaseResultWithData(
                data={"item_id": item.id, "desc": item.desc},
                status_code=HTTPStatus.OK,
                message="Cart item description updated successfully"
            )

        except CartItem.DoesNotExist:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.NOT_FOUND,
                message="Cart item not found"
            )
        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to update cart description: {str(e)}"
            )
