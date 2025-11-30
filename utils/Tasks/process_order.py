
from celery import shared_task
from utils.decorators import checkBackgroundFeatureFlag
from utils.enum import TransactionChannel, TransactionStatus, TransactionType
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail


@checkBackgroundFeatureFlag()
@shared_task
def process_paystack_order(order_id, reference, data):
    """
    Process order after successful Paystack payment verification.
    """
    
    from apps.users.models import Transaction
    from apps.aso.models import Order, OrderItem, OrderTracking, PaymentDetail, ShippingAddress
    
    
    order = Order.objects.get(id=order_id, is_deleted=False)
    user = order.user
    cart = user.cart
    # 2. Create Order Items
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.current_price,
            desc = item.desc
        )

    # 3. Save Shipping Address
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
        amount = cart.total(),
    )
    
    OrderTracking.objects.create(
        order = order,
        date = timezone.now(),
        description = "Order has been placed and ready for processing."
    )

    Transaction.objects.create(
        user=user,
        amount=cart.total(),
        transaction_type=TransactionType.PURCHASE.value,
        reference=reference,
        channel=TransactionChannel.PAYSTACK.value,
        status=TransactionStatus.SUCCESS.value
    )

    user.referral_used_purchase = True
    user.save(update_fields=["referral_used_purchase"])

    # 4. Delete Cart and Items
    cart.items.all().delete()
    cart.delete()
    
    send_mail(
        subject="New Order Confirmation",
        message=f"A new order has been placed.\n\nOrder ID: {order.id}\nOrder Number: {order.order_number}\nAmount: {order.total}\nCreated At: {order.created_at}\nLink: {settings.BASE_URL}/admin/orders.html",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],
    )
    
    
    return True