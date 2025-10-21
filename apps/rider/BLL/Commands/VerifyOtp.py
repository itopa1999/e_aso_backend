from http import HTTPStatus
from django.utils import timezone
from apps.aso.models import Order
from utils.base_result import BaseResult, BaseResultWithData
from apps.users.models import UserVerification
from utils.log_helpers import OperationLogger


class VerifyOtpCommand:
    @staticmethod
    def execute(request, order_number, otp):
        op = OperationLogger("VerifyOtpCommand", order_number=order_number, otp=otp)
        op.start()
        try:
            order = Order.objects.get(order_number=order_number, is_deleted=False)
        except Order.DoesNotExist:
            op.fail("Order not found")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.NOT_FOUND, 
                message="Order not found"
            )

        try:
            verification = UserVerification.objects.get(user=order.user, is_deleted=False)
        except UserVerification.DoesNotExist:
            op.fail("No OTP found for user")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST, 
                message="No OTP found for this user"
            )

        if timezone.now() > verification.created_at + timezone.timedelta(minutes=10):
            op.fail("OTP expired")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST, 
                message="OTP expired"
            )

        if int(verification.token) != int(otp):
            op.fail("Invalid OTP")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST, 
                message="Invalid OTP"
            )
        verification.is_verified = True
        verification.save()
        
        # Fetch shipping address
        shipping = getattr(order, 'shipping_address', None)

        # Fetch order items
        items = order.items.select_related('product').all()
        order_items_data = [
            {
                "product_id" : item.product.id,
                "product": item.product.title,
                "quantity": item.quantity,
                "price": f"₦{item.price:,.0f}",
                "total_price": f"₦{item.total_price():,.0f}",
                "image": request.build_absolute_uri(item.product.main_image.url) if item.product.main_image else None,
                "desc": item.desc
            }
            for item in items
        ]

        # Prepare response data
        order_data = {
            "message": "OTP verified successfully",
            "order_details": {
                "order_id": order.order_number,
                "customer": f"{order.user.first_name} {order.user.last_name}" if order.user.last_name else "Not Set",
                "delivery_address": f"{shipping.address}, {shipping.city}, {shipping.state}" if shipping else "",
                "contact": shipping.phone if shipping.phone else shipping.alt_phone,
                "order_date": order.created_at.strftime("%b %d, %Y"),
                "total_amount": f"₦{order.total:,.0f}",
                "other_info": order.other_info,
                "items": order_items_data
            }
        }
        
        op.success(f"OTP verified successfully for order {order_number}")
        
        return BaseResultWithData(
            data=order_data,
            status_code=HTTPStatus.OK, 
            message="OTP verified successfully"
        )