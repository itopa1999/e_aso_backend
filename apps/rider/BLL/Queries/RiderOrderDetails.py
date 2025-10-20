from http import HTTPStatus
from apps.aso.models import Order
from utils.base_result import BaseResult, BaseResultWithData


class RiderOrderDetailsQuery:
    @staticmethod
    def execute(order_number, request):
        try:
            order = Order.objects.get(order_number=order_number, is_deleted=False)
        except Order.DoesNotExist:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.NOT_FOUND, 
                message="Order not found"
            )

        shipping = getattr(order, 'shipping_address', None)
        items = order.items.select_related('product').all()

        order_items_data = [
            {
                "product_id": i.product.id,
                "product": i.product.title,
                "quantity": i.quantity,
                "price": f"₦{i.price:,.0f}",
                "total_price": f"₦{i.total_price():,.0f}",
                "image": request.build_absolute_uri(i.product.main_image.url) if i.product.main_image else None,
                "desc": i.desc
            } for i in items
        ]

        order_data = {
            "order_id": order.order_number,
            "customer": f"{order.user.first_name} {order.user.last_name}" if order.user.last_name else "Not Set",
            "delivery_address": f"{shipping.address}, {shipping.city}, {shipping.state}" if shipping else "",
            "contact": shipping.phone if shipping.phone else shipping.alt_phone,
            "order_date": order.created_at.strftime("%b %d, %Y"),
            "total_amount": f"₦{order.total:,.0f}",
            "other_info": order.other_info,
            "items": order_items_data
        }

        return BaseResultWithData(
            data = order_data,
            status_code=HTTPStatus.OK, 
            message= "Success"
        )
