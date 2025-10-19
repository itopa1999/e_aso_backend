from http import HTTPStatus
from django.conf import settings
from django.shortcuts import redirect
from apps.aso.paystack import validate
from utils.base_result import BaseResultWithData


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

            return redirect(redirect_url)
        else:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message=result.get("error", "Payment verification failed.")
            )
