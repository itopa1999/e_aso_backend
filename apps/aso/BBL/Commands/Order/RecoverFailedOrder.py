from rest_framework import status
from apps.aso.models import Order, PaymentDetail, ShippingAddress
from utils.enum import PaymentStatus
from utils.Tasks.process_order import process_paystack_order
from utils.base_result import BaseResult


class RecoverFailedOrderCommand:
    """
    Command to retry processing a failed order.
    Used when a Celery task fails but the payment has been confirmed.
    """

    @staticmethod
    def execute(user, order_id):
        """
        Retry processing a failed order.
        
        Args:
            user: The authenticated user
            order_id: The ID of the failed order
            
        Returns:
            BaseResult: Contains success status and response data
        """
        try:
            # Get the failed order
            order = Order.objects.get(
                id=order_id,
                user=user,
                is_deleted=False,
                payment_status=PaymentStatus.FAILED.name.lower()
            )
            
            # Get the associated payment details
            payment_detail = PaymentDetail.objects.filter(order=order).first()
            if not payment_detail:
                return BaseResult(
                    success=False,
                    message="Payment details not found for this order",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the shipping address
            shipping_addr = ShippingAddress.objects.filter(order=order).first()
            if not shipping_addr:
                return BaseResult(
                    success=False,
                    message="Shipping address not found for this order",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Reconstruct the shipping data
            data = {
                "first_name": shipping_addr.first_name,
                "last_name": shipping_addr.last_name,
                "address": shipping_addr.address,
                "apartment": shipping_addr.apartment,
                "city": shipping_addr.city,
                "state": shipping_addr.state,
                "phone": shipping_addr.phone,
                "alt_phone": shipping_addr.alt_phone,
                "otherInfo": order.other_info,
                "payment_type": payment_detail.method,
            }
            
            # Requeue the background task
            process_paystack_order.delay(order.id, order.payment_reference, data)
            
            # Update order status back to pending
            order.payment_status = PaymentStatus.PENDING.name.lower()
            order.save(update_fields=['payment_status'])
            
            return BaseResult(
                success=True,
                message="Order processing has been retried. Please check again in a few moments.",
                data={"order_id": order.id},
                status_code=status.HTTP_200_OK
            )
            
        except Order.DoesNotExist:
            return BaseResult(
                success=False,
                message="Order not found or is not in failed state",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return BaseResult(
                success=False,
                message=f"Error retrying order: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
