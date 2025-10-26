from decimal import Decimal
from http import HTTPStatus
from django.conf import settings
from apps.aso.models import Cart
from apps.aso.paystack import initiate
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger


class PlaceOrderCommand:
    @staticmethod
    def execute(request, shipping_data):
        op = OperationLogger(
            "PlaceOrderCommand",
            user=request.user.id if request.user and request.user.is_authenticated else "Anonymous"
        )
        op.start()
        
        try:
            # Get user cart
            try:
                cart = request.user.cart
            except Cart.DoesNotExist:
                op.fail("Cart not found", e)
                return BaseResultWithData(
                    data=None,
                    status_code=HTTPStatus.BAD_REQUEST,
                    message="Cart not found."
                )

            expected_total = cart.total()
            user_total = Decimal(shipping_data["total"])

            # Validate totals
            if expected_total != user_total:
                op.fail(f"Total mismatch. Expected ₦{expected_total}, got ₦{user_total}")
                return BaseResultWithData(
                    data=None,
                    status_code=HTTPStatus.BAD_REQUEST,
                    message=f"Total mismatch. Expected ₦{expected_total}, got ₦{user_total}"
                )
                
            # if request.user.referral_used_purchase:
            #     return BaseResultWithData(
            #         data=None,
            #         status_code=HTTPStatus.BAD_REQUEST,
            #         message="Referral discount has already been used for a purchase."
            #     )

            # Initialize payment
            checkout_link = initiate(request, user=request.user, cart_id=cart.id, data=shipping_data)
            if not checkout_link:
                op.fail("Payment initialization failed.")
                return BaseResultWithData(
                    data=None,
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    message="Payment initialization failed."
                )
            op.success("Order initialized successfully.")
            return BaseResultWithData(
                data={"checkout_url": checkout_link},
                status_code=HTTPStatus.OK,
                message="Order initialized successfully."
            )

        
        except Exception as e:
            op.fail("Failed to place order", e)
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to place order: {str(e)}"
            )
