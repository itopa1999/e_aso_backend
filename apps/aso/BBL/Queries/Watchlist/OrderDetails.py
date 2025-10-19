from apps.aso.models import Order
from apps.aso.serializers import OrderDetailSerializer
from http import HTTPStatus
from utils.base_result import BaseResultWithData

class OrderDetailQuery:

    @staticmethod
    def query(user, order_id):
        try:
            order = Order.objects.get(user=user, id=order_id, is_deleted = False)
            serializer = OrderDetailSerializer(order)
            return BaseResultWithData(
                data=serializer.data,
                status_code=HTTPStatus.OK,
                message="Order details fetched successfully"
            )
        except Order.DoesNotExist:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.NOT_FOUND,
                message="Order not found"
            )
        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to fetch order details: {str(e)}"
            )
