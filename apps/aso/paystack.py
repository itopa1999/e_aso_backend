from django.utils import timezone
import json
import secrets
from django.conf import settings
from django.urls import reverse
import requests as req
from django.db import transaction

from apps.aso.models import Cart, Order, OrderItem, OrderTracking
from utils.Tasks.process_order import process_paystack_order
from utils.enum import PaymentGateway, PaymentStatus
from utils.log_helpers import OperationLogger

def initiate(request, user, cart_id, data, order_id=None):
    op = OperationLogger(
        "PaystackInitiate",
        user=user.id if user else "Anonymous",
        cart_id=cart_id,
        order_id=order_id,
        data=data
    )
    op.start()
    
    with transaction.atomic():    
        ref = secrets.token_urlsafe(15)
        
        # If order_id is provided (retry), fetch existing order
        if order_id:
            try:
                order = Order.objects.get(id=order_id, is_deleted=False)
                amount = int(float(order.total)) * 100
            except Order.DoesNotExist:
                op.fail("Order not found for retry")
                return None
        else:
            # New order flow
            amount = int(float(data["total"])) * 100
        
        redirect_url = request.build_absolute_uri(
            reverse('paystack-confirm-subscription', kwargs={"reference": ref})
        )
            
        paystack_data = {
            "email": user.email,
            "amount": amount,
            "reference": ref,
            "metadata": {
                "data": json.loads(json.dumps(data, default=str)),
                "cart_id": cart_id
            },
            "callback_url": redirect_url,
        }
        
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        paystack_url = f"{settings.PAYSTACK_INITIALIZE_URL}"
        response = req.post(paystack_url, headers=headers, json=paystack_data)

        if response.status_code == 200:
            # If retry (order_id provided), just update reference and return URL
            if order_id:
                order.payment_reference = ref
                order.payment_status = PaymentStatus.PENDING.name.lower()
                order.save(update_fields=['payment_reference', 'payment_status'])
                op.success(f"Paystack retry initialized for order {order.order_number}")
                return response.json()["data"]["authorization_url"]
            
            # New order flow
            cart = Cart.objects.get(id=cart_id, is_deleted=False)
            
            order = Order.objects.create(
                user=user,
                subtotal=cart.subtotal(),
                shipping_fee=cart.shipping_cost(),
                discount=cart.discount(),
                total=cart.total(),
                other_info=data.get("otherInfo"),
                payment_status=PaymentStatus.PENDING.name.lower(),
                payment_reference=ref,
                payment_method=PaymentGateway.PAYSTACK.value,
            )
            
            # Create order items from cart items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.current_price,
                    desc=cart_item.desc
                )
            
            # Process order immediately after creation
            try:
                shipping_data = data
                
                process_paystack_order(order.id, ref, shipping_data)
                
                # 4. Delete Cart and Items
                cart.items.all().delete()
                cart.delete()
        
                op.success(f"Paystack initialization successful, order {order.order_number} created and processing")
            except Exception as e:
                order.payment_status = PaymentStatus.FAILED.name.lower()
                order.save(update_fields=['payment_status'])
                op.fail(f"Order processing failed: {str(e)}")
                return None
            
            return response.json()["data"]["authorization_url"]

        op.fail("Paystack initialization failed")
        return None
            


def validate(reference):
    op = OperationLogger("PaystackValidate", reference=reference)
    op.start()
    
    url = f"{settings.PAYSTACK_VERIFY_URL}/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }
    
    try:
        response = req.get(url, headers=headers)
        result = response.json()
        
        # Check if verification is successful
        if response.status_code != 200 or result["data"]["status"] != "success":
            op.fail("Paystack verification failed")
            return {"success": False, "error": "Invalid or unsuccessful transaction."}
        
        with transaction.atomic():
            # Find existing order by payment reference
            order = Order.objects.filter(
                payment_reference=reference,
                payment_method=PaymentGateway.PAYSTACK.value,
            ).first()
            
            if not order:
                op.fail("Order not found for this payment reference")
                return {"success": False, "error": "Order not found for this payment reference."}
            
            # If order already confirmed, return it
            if order.payment_status == PaymentStatus.CONFIRMED.name.lower():
                op.success("Order already confirmed for this reference (retry)")
                return {
                    "success": True,
                    "message": "Payment already confirmed.",
                    "order": {
                        "id": order.id,
                        "order_number": order.order_number,
                        "amount": float(order.total),
                        "created_at": order.created_at
                    }
                }
            
            # Update order status to confirmed and process
            try:
                OrderTracking.objects.create(
                    order = order,
                    date = timezone.now(),
                    description = "Order has been placed and ready for processing."
                )
                order.payment_status = PaymentStatus.CONFIRMED.name.lower()
                order.save(update_fields=['payment_status'])
                op.success("Order confirmed")
            except Exception as e:
                order.payment_status = PaymentStatus.FAILED.name.lower()
                order.save(update_fields=['payment_status'])
                op.fail(f"Status update failed: {str(e)}")
                return {"success": False, "error": f"Order status update failed: {str(e)}"}
            
        op.success("Transaction validated and order confirmed")
        return {
            "success": True,
            "message": "Payment confirmed successfully.",
            "order": {
                "id": order.id,
                "order_number": order.order_number,
                "amount": float(order.total),
                "created_at": order.created_at
            }
        }
    except Exception as e:
        op.fail(f"Validation error: {str(e)}")
        return {"success": False, "error": f"Validation error: {str(e)}"}
