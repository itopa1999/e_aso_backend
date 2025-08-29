from django.utils import timezone
import json
import secrets
from django.conf import settings
from django.urls import reverse
import requests as req
from django.db import transaction

from aso.models import Cart, Order, OrderItem, OrderTracking, PaymentDetail, ShippingAddress

def initiate(request, user, cart_id, data):
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
        return response.json()["data"]["authorization_url"]

    return None
            


def validate(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }
    response = req.get(url, headers=headers)
    result = response.json()
    # Step 2: Check if verification is successful
    if response.status_code == 200 and result['data']['status'] == 'success':
        metadata = result['data'].get('metadata', {})
        cart_id = metadata.get('cart_id')
        data = metadata.get('data', {})
        
        try:
            with transaction.atomic():
                cart = Cart.objects.get(id=cart_id)
                user = cart.user

                # 1. Create Order
                order = Order.objects.create(
                    user=user,
                    subtotal=cart.subtotal(),
                    shipping_fee=cart.shipping_cost(),
                    discount=cart.discount(),
                    total=cart.total(),
                    other_info = data.get("otherInfo")
                )

                # 2. Create Order Items
                for item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.current_price,  # snapshot
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
                    method = "Paystack"
                )
                
                OrderTracking.objects.create(
                    order = order,
                    date = timezone.now(),
                    description = "Order has been placed and ready for processing."
                )

                # 4. Delete Cart and Items
                cart.items.all().delete()
                cart.delete()
                
                
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
        except Exception as e:
            return {"success": False, "error": f"Failed to process transaction: {str(e)}"}
    
    return {"success": False, "error": "Subscription was unsuccessful or invalid reference."}
