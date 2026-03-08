
from celery import shared_task
from celery.utils.log import get_task_logger
from utils.decorators import checkBackgroundFeatureFlag
from utils.enum import TransactionChannel, TransactionStatus, TransactionType, PaymentStatus
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

logger = get_task_logger(__name__)


@checkBackgroundFeatureFlag()
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_paystack_order(self, order_id, reference, data):
    """
    Process order after successful Paystack payment verification.
    Handles order items, shipping address, payment details, and transaction records.
    Retries up to 3 times if any step fails.
    """
    
    from apps.users.models import Transaction
    from apps.aso.models import Order, PaymentDetail, ShippingAddress
    
    try:
        order = Order.objects.get(id=order_id, is_deleted=False)
        user = order.user
        
        logger.info(f"Processing order {order_id} for user {user.id}")
        
        # Save Shipping Address
        ShippingAddress.objects.create(
            order=order,
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            address=data.get("address"),
            apartment=data.get("apartment", ""),
            city=data.get("city"),
            state=data.get("state"),
            phone=data.get("phone"),
            alt_phone=data.get("alt_phone"),
        )
        
        PaymentDetail.objects.create(
            order=order,
            method = data.get("payment_type", "Paystack"),
            amount = order.total,
        )

        Transaction.objects.create(
            user=user,
            amount=order.total,
            transaction_type=TransactionType.PURCHASE.value,
            reference=reference,
            channel=TransactionChannel.PAYSTACK.value,
            status=TransactionStatus.SUCCESS.value
        )

        user.referral_used_purchase = True
        user.save(update_fields=["referral_used_purchase"])

        
        
        logger.info(f"Order {order_id} processed successfully")
        
        send_mail(
            subject="Order Initiated",
            message=f"An order has been initiated.\n\nOrder ID: {order.id}\nOrder Number: {order.order_number}\nAmount: {order.total}\nCreated At: {order.created_at}\nLink: {settings.BASE_URL}/admin/orders.html",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
        )
        
        return {"status": "success", "order_id": order_id, "message": "Order processed successfully"}
        
    except Order.DoesNotExist as e:
        logger.error(f"Order {order_id} not found: {str(e)}")
        # Update order status to failed if it exists
        try:
            order = Order.objects.get(id=order_id)
            order.payment_status = PaymentStatus.FAILED.name.lower()
            order.save(update_fields=['payment_status'])
        except Order.DoesNotExist:
            pass
        return {"status": "failed", "error": "Order not found", "order_id": order_id}
        
    except Exception as e:
        logger.error(f"Error processing order {order_id}: {str(e)}")
        
        # Retry up to 3 times with 60-second delay
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task for order {order_id}, attempt {self.request.retries + 1}")
            raise self.retry(exc=e)
        else:
            # All retries exhausted - mark order as failed
            try:
                order = Order.objects.get(id=order_id)
                order.payment_status = PaymentStatus.FAILED.name.lower()
                order.save(update_fields=['payment_status'])
                logger.error(f"Order {order_id} marked as FAILED after {self.max_retries} retries")
            except Order.DoesNotExist:
                pass
            
            # Alert admin
            send_mail(
                subject=f"⚠️ ORDER PROCESSING FAILED - {order_id}",
                message=f"Order {order_id} failed to process after {self.max_retries} retries.\n\nReference: {reference}\nError: {str(e)}\n\nPlease check manually.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
            )
            return {"status": "failed", "error": "Order processing failed after retries", "order_id": order_id}