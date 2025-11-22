from django.utils import timezone
import json
import secrets
from django.conf import settings
from django.urls import reverse
import requests as req
from django.db import transaction

from apps.aso.models import Cart, Order, OrderItem, OrderTracking, PaymentDetail, ShippingAddress
from apps.users.models import Transaction
from utils.Tasks.process_order import process_paystack_order
from utils.enum import TransactionChannel, TransactionStatus, TransactionType
from utils.log_helpers import OperationLogger

def initiate(request, user, cart_id, data):
    op = OperationLogger(
        "PaystackInitiate",
        user=user.id if user else "Anonymous",
        cart_id=cart_id,
        data=data
    )
    op.start()
    
    with transaction.atomic():    
        ref = secrets.token_urlsafe(15)
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
                "cart_id":cart_id
            },
            "callback_url": redirect_url,
        }
        
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        paystack_url = "https://api.paystack.co/transaction/initialize"
        response = req.post(paystack_url, headers=headers, json=paystack_data)

        if response.status_code == 200:
            op.success("Paystack initialization successful")
            return response.json()["data"]["authorization_url"]

        op.fail("Paystack initialization failed")
        return None
            


def validate(reference):
    op = OperationLogger("PaystackValidate", reference=reference)
    op.start()
    
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }
    
    try:
        response = req.get(url, headers=headers)
        result = response.json()
        # Step 2: Check if verification is successful
        if response.status_code != 200 or result["data"]["status"] != "success":
            op.fail("Paystack verification failed")
            return {"success": False, "error": "Invalid or unsuccessful transaction."}
        
        metadata = result['data'].get('metadata', {})
        cart_id = metadata.get('cart_id')
        data = metadata.get('data', {})
                
        with transaction.atomic():
            cart = Cart.objects.get(id=cart_id, is_deleted=False)
            user = cart.user

            order = Order.objects.create(
                user=user,
                subtotal=cart.subtotal(),
                shipping_fee=cart.shipping_cost(),
                discount=cart.discount(),
                total=cart.total(),
                other_info=data.get("otherInfo"),
                telegram_user_chat_id=data.get("telegram_user_chat_id"),
            )

            # Run the task in background
            process_paystack_order(order.id, reference, data)
            
        op.success("Transaction validated and order created")
        return {
            "success": True,
            "message": "Subscription was successful.",
            "order": {
                "id": order.id,
                "order_number": order.order_number,
                "amount": float(order.total),
                "created_at": order.created_at
            }
        }
    except Cart.DoesNotExist as e:
        op.fail("Cart not found")
        return {"success": False, "error": "Cart not found or already processed."}
