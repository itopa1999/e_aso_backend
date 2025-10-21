from http import HTTPStatus
from django.db.models import Q
from apps.aso.models import Order
from utils.base_result import BaseResult, BaseResultWithData


class RiderDashboardQuery:
    @staticmethod
    def query(rider, search=None):
        try:
            profile_data = {
                "name": f"{rider.first_name} {rider.last_name}",
                "rider_id": rider.rider_number,
                "deliveries_count": Order.objects.filter(
                    dispatcher=rider,
                    delivery_date__isnull=False,
                    is_deleted=False
                ).count()
            }

            recent_orders = Order.objects.filter(
                dispatcher=rider,
                delivery_date__isnull=False,
                is_deleted=False
            )

            if search:
                recent_orders = recent_orders.filter(
                    Q(user__first_name__icontains=search) |
                    Q(user__last_name__icontains=search) |
                    Q(order_number__icontains=search) |
                    Q(total__icontains=search)
                )

            recent_orders = recent_orders.order_by('-delivery_date')

            return BaseResultWithData(
                status_code=HTTPStatus.OK,
                message="Success",
                data={"profile": profile_data, "recent_deliveries": recent_orders}
            )
        except Exception as e:
            return BaseResultWithData(
                data = None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=str(e)
            )

