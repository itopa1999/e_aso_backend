from http import HTTPStatus
from apps.aso.models import Order
from apps.aso.serializers import OrderSerializer
from utils.base_result import BaseResultWithData

class UserOrderListQuery:

    @staticmethod
    def query(user):
        try:
            orders = Order.objects.filter(user=user, is_deleted = False).prefetch_related('items', 'tracking_events').order_by('-created_at')
            serializer = OrderSerializer(orders, many=True)
            return BaseResultWithData(
                data=serializer.data,
                status_code=HTTPStatus.OK,
                message="User orders fetched successfully"
            )
        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to fetch user orders: {str(e)}"
            )
