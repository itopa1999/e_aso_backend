import textwrap
from http import HTTPStatus
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from apps.aso.models import Order, OrderFeedBack, OrderTracking
from utils.base_result import BaseResult, BaseResultWithData
from utils.email_sender import send_custom_email
from utils.log_helpers import OperationLogger


class MarkOrderAsDeliveredCommand:
    @staticmethod
    def execute(order_number, rider, delivery_notes, stars):
        op = OperationLogger("MarkOrderAsDeliveredCommand", order_number=order_number, rider=rider)
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
            
        if not stars or not str(stars).isdigit() or not (1 <= int(stars) <= 5):
            op.fail("Invalid star rating")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST, 
                message="Please provide a valid star rating between 1 and 5"
            )

        OrderTracking.objects.create(
            order=order,
            status="delivered",
            date=timezone.now(),
            description=delivery_notes or "Order marked as delivered.",
            completed=True
        )

        OrderFeedBack.objects.update_or_create(
            order=order,
            defaults={"stars": int(stars), "comment": delivery_notes}
        )

        order.dispatcher = rider
        order.delivery_date = timezone.now()
        order.save()
        
        send_custom_email(
            subject="Your Order Has Been Delivered",
            recipient_email=order.user.email,
            message=f"""
            Your order {order.order_number} has been successfully delivered.

            Thank you for shopping with us.
            """,
            greeting_name=order.user.first_name or "Valued Customer"
        )
        
        op.success("Order marked as delivered successfully")
        
        return BaseResultWithData(
                data={"order_number": order.order_number},
                status_code=HTTPStatus.OK, 
                message="Order marked as delivered successfully"
            )