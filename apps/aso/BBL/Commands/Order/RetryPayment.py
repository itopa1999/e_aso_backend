from http import HTTPStatus
from apps.aso.models import Order, Cart
from apps.aso.paystack import initiate as paystack_initiate
from apps.aso.paystack import validate as paystack_validate
from apps.aso.flutterwave import validate as flutter_validate
from apps.aso.flutterwave import initiate as flutterwave_initiate
from utils.base_result import BaseResultWithData
from utils.enum import PaymentGateway, PaymentStatus
from utils.log_helpers import OperationLogger


class RetryPaymentCommand:
    @staticmethod
    def execute(request, order_id):
        op = OperationLogger(
            "RetryPaymentCommand",
            order_id=order_id,
            user=request.user.id if request.user and request.user.is_authenticated else "Anonymous"
        )
        op.start()
        
        try:
            order = Order.objects.get(id=order_id, is_deleted=False, user=request.user)
        except Order.DoesNotExist:
            op.fail("Order not found")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.NOT_FOUND,
                message="Order not found."
            )
            
        payment_method = order.payment_method
        
        # Rule 1: Check if payment status is failed, cancelled, or pending
        if order.payment_status not in [
            PaymentStatus.FAILED.name.lower(),
            PaymentStatus.CANCELLED.name.lower(),
            PaymentStatus.PENDING.name.lower()
        ]:
            op.fail(f"Cannot retry payment for order with status: {order.payment_status}")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message=f"Cannot retry payment. Order payment status is already {order.payment_status}."
            )
        
        # Rule 2: If order has a payment reference, try to validate it
        if order.payment_reference:
            # Validate based on payment method
            if payment_method.lower() == PaymentGateway.PAYSTACK.value.lower():
                result = paystack_validate(order.payment_reference)
            elif payment_method.lower() == PaymentGateway.FLUTTERWAVE.value.lower():
                result = flutter_validate(order.payment_reference)
            else:
                op.fail(f"Validation not supported for payment method: {order.payment_method}")
                return BaseResultWithData(
                    data=None,
                    status_code=HTTPStatus.BAD_REQUEST,
                    message=f"Validation not supported for {order.payment_method}. Please contact support."
                )
            
            # If validation failed
            if not result.get("success"):
                # Continue to reinitiate below
                pass
            else:
                op.success(f"Payment already validated for reference {order.payment_reference}")
                return BaseResultWithData(
                    data=result.get("order"),
                    status_code=HTTPStatus.OK,
                    message=result.get("message", "Payment already confirmed.")
                )
        
        # Rule 3: If no reference or validation failed, reinitiate payment
        # Initiate payment based on payment method
        try:
            if payment_method.lower() == PaymentGateway.PAYSTACK.value.lower():
                checkout_url = paystack_initiate(request, user=request.user, cart_id=None, data=None, order_id=order.id)
            elif payment_method.lower() == PaymentGateway.FLUTTERWAVE.value.lower():
                checkout_url = flutterwave_initiate(request, user=request.user, cart_id=None, data=None, order_id=order.id)
            elif payment_method.lower() == PaymentGateway.MONNIFY.value.lower():
                # TODO: Implement Monnify payment logic
                op.fail(f"Monnify retry not yet implemented")
                return BaseResultWithData(
                    data=None,
                    status_code=HTTPStatus.BAD_REQUEST,
                    message="Monnify payment retry is not yet implemented. Please contact support."
                )
            else:
                op.fail(f"Unknown payment method: {order.payment_method}")
                return BaseResultWithData(
                    data=None,
                    status_code=HTTPStatus.BAD_REQUEST,
                    message=f"Payment method {order.payment_method} is not supported."
                )
            
            if not checkout_url:
                op.fail("Payment reinitialization failed")
                return BaseResultWithData(
                    data=None,
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    message="Failed to reinitiate payment. Please try again."
                )
            
            op.success(f"Payment reinitialized successfully for order {order.order_number}")
            return BaseResultWithData(
                data={"checkout_url": checkout_url},
                status_code=HTTPStatus.OK,
                message="Payment link generated. Please complete the payment."
            )
            
        except Exception as e:
            op.fail(f"Payment reinitialization error: {str(e)}")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Error reinitializing payment: {str(e)}"
            )
