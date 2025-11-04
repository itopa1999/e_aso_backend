from http import HTTPStatus
from django.conf import settings
from django.shortcuts import redirect
from apps.aso.paystack import validate
from utils.base_result import BaseResultWithData
from django.core.mail import send_mail

class PaystackConfirmQuery:
    @staticmethod
    def execute(reference):
        if not reference:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message="No reference provided"
            )

        result = validate(reference)
        if result.get("success"):
            order = result.get("order")
            redirect_url = (
                f"{settings.BASE_URL}/order-success.html"
                f"?order_id={order['id']}"
                f"&order_number={order['order_number']}"
                f"&amount={order['amount']}"
                f"&created_at={order['created_at']}"
            )
            
            # SCHEDULE TASK
            send_mail(
                subject="New Order Confirmation",
                message=f"A new order has been placed.\n\nOrder ID: {order['id']}\nOrder Number: {order['order_number']}\nAmount: {order['amount']}\nCreated At: {order['created_at']}\nLink: {f"{settings.BASE_URL}/admin/orders.html"}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
            )

            return redirect(redirect_url)
        else:
            redirect_url = (
                f"{settings.BASE_URL}/order-failed.html"
                f"?reference={reference}"
                f"&error={result.get('error', 'Transaction failed')}"
            )
            
            
            
            return redirect(redirect_url)
