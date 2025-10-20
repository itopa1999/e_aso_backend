from http import HTTPStatus
import random
from django.utils import timezone
from apps.aso.models import Order, OrderTracking
from utils.base_result import  BaseResultWithData
from apps.users.models import UserVerification
from utils.email_sender import send_custom_email


class SendOtpCommand:
    @staticmethod
    def execute(order_number):
        try:
            order = Order.objects.get(order_number=order_number, is_deleted=False)
        except Order.DoesNotExist:
            return BaseResultWithData(
                data = None,
                status_code=HTTPStatus.NOT_FOUND,
                message="Order not found"
            )

        if OrderTracking.objects.filter(order=order, status__in=["delivered", "cancelled"], is_deleted=False).exists():
            return BaseResultWithData(
                data = None, 
                status_code=HTTPStatus.BAD_REQUEST, 
                message="Order already delivered or cancelled, OTP not required.")

        if not OrderTracking.objects.filter(order=order, status="in_transit", is_deleted=False).exists():
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST, 
                message="Order is not currently in transit, OTP cannot be sent.")

        user = order.user
        verification, _ = UserVerification.objects.get_or_create(user=user, is_deleted=False)
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

        return BaseResultWithData(
            data=None,
            status_code=HTTPStatus.OK, 
            message="OTP sent to customer's email")
