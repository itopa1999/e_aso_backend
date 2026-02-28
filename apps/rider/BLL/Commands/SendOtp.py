from http import HTTPStatus
import random
from django.utils import timezone
from apps.aso.models import Order, OrderTracking
from utils.base_result import  BaseResultWithData
from apps.users.models import UserVerification
from utils.email_sender import send_custom_email
from utils.log_helpers import OperationLogger


class SendOtpCommand:
    @staticmethod
    def execute(order_number):
        op = OperationLogger("SendOtpCommand", order_number=order_number)
        op.start()
        try:
            order = Order.objects.get(order_number=order_number, is_deleted=False)
        except Order.DoesNotExist:
            op.fail("Order not found")
            return BaseResultWithData(
                data = None,
                status_code=HTTPStatus.NOT_FOUND,
                message="Order not found"
            )

        if OrderTracking.objects.filter(order=order, status__in=["delivered", "cancelled"], is_deleted=False).exists():
            op.fail("OTP not required (order already delivered or cancelled)")
            return BaseResultWithData(
                data = None, 
                status_code=HTTPStatus.BAD_REQUEST, 
                message="Order already delivered or cancelled, OTP not required.")

        if not OrderTracking.objects.filter(order=order, status="in_transit", is_deleted=False).exists():
            op.fail("OTP cannot be sent (order not in transit)")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST, 
                message="Order is not currently in transit, OTP cannot be sent.")

        user = order.user
        # Use get_or_create with only user parameter
        verification, _ = UserVerification.objects.get_or_create(user=user)
        verification.token = str(random.randint(100000, 999999))
        verification.created_at = timezone.now()
        verification.is_verified = False
        verification.save()
        
        send_custom_email(
            subject="Your Delivery OTP",
            recipient_email=user.email,
            message=f"""
            Your OTP is: {verification.token}

            This link expires in 10 minutes.
            If you didn’t request this login, please ignore this email.
            """,
            greeting_name=user.first_name or "Valued Customer"
        )

        op.success(f"OTP sent successfully to {user.email}")
        return BaseResultWithData(
            data=None,
            status_code=HTTPStatus.OK, 
            message="OTP sent to customer's email")
