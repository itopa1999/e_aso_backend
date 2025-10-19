from http import HTTPStatus
from apps.aso.models import Cart
from apps.aso.serializers import CartDetailSerializer
from utils.base_result import BaseResultWithData


class GetCartDetailQuery:
    @staticmethod
    def query(user):
        try:
            cart, created = Cart.objects.get_or_create(user=user, is_deleted=False)

            serializer = CartDetailSerializer(cart)
            return BaseResultWithData(
                data=serializer.data,
                status_code=HTTPStatus.OK,
                message="Cart detail retrieved successfully"
            )

        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to fetch cart details: {str(e)}"
            )
