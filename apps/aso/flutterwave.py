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
from utils.enum import TransactionChannel, TransactionStatus, TransactionType, PaymentGateway, PaymentStatus
from utils.log_helpers import OperationLogger


def initiate(request, user, cart_id, data):
    """
    Initialize Flutterwave payment
    """
    op = OperationLogger(
        "FlutterwaveInitiate",
        user=user.id if user else "Anonymous",
        cart_id=cart_id,
        data=data
    )
    op.start()
    
    with transaction.atomic():    
        ref = secrets.token_urlsafe(15)
        amount = float(data["total"])
        
        redirect_url = request.build_absolute_uri(
            reverse('flutterwave-confirm', kwargs={"reference": ref})
        )
            
        flutterwave_data = {
            "tx_ref": ref,
            "amount": amount,
            "currency": "NGN",
            "customer": {
                "email": user.email,
                "phonenumber": data.get("phone", ""),
                "name": f"{data.get('first_name', '')} {data.get('last_name', '')}"
            },
            "customizations": {
                "title": "Esther's Fabrics Order Payment",
                "description": f"Payment for order {ref}",
                "logo": ""
            },
            "meta": {
                "first_name": data.get("first_name", ""),
                "last_name": data.get("last_name", ""),
                "address": data.get("address", ""),
                "city": data.get("city", ""),
                "state": data.get("state", ""),
                "phone": data.get("phone", ""),
                "alt_phone": data.get("alt_phone", ""),
                "otherInfo": data.get("otherInfo", ""),
                "telegram_user_chat_id": data.get("telegram_user_chat_id", ""),
                "payment_type": data.get("payment_type", "Flutterwave"),
                "cart_id": cart_id,
            },
            "redirect_url": redirect_url,
        }
        
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        flutterwave_url = "https://api.flutterwave.com/v3/payments"
        response = req.post(flutterwave_url, headers=headers, json=flutterwave_data)

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("status") == "success":
                op.success("Flutterwave initialization successful")
                return response_data["data"]["link"]

        op.fail("Flutterwave initialization failed")
        return None
            

def validate(reference):
    """
    Validate Flutterwave payment using transaction reference
    """
    op = OperationLogger("FlutterwaveValidate", reference=reference)
    op.start()
    
    # Get the transaction details from Flutterwave
    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"
    }
    
    try:
        # Flutterwave requires querying by tx_ref or transaction ID
        url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={reference}"
        response = req.get(url, headers=headers)
        result = response.json()
        
        print("Flutterwave validation response:", result)
        
        # Check if verification is successful
        if response.status_code != 200 or result["status"] != "success":
            op.fail("Flutterwave verification failed")
            return {"success": False, "error": "Invalid or unsuccessful transaction."}
        
        transaction_data = result["data"]
        
        # Verify payment was successful
        if transaction_data.get("status") != "successful":
            op.fail("Transaction status is not successful")
            return {"success": False, "error": "Transaction not successful."}
        
        meta = transaction_data.get("meta", {})
        cart_id = meta.get("cart_id") if isinstance(meta, dict) else None
        
        # Extract shipping data from meta
        shipping_data = {
            "first_name": meta.get("first_name", ""),
            "last_name": meta.get("last_name", ""),
            "address": meta.get("address", ""),
            "city": meta.get("city", ""),
            "state": meta.get("state", ""),
            "phone": meta.get("phone", ""),
            "alt_phone": meta.get("alt_phone", ""),
            "otherInfo": meta.get("otherInfo", ""),
            "telegram_user_chat_id": meta.get("telegram_user_chat_id", ""),
            "payment_type": meta.get("payment_type", "Flutterwave"),
        } if isinstance(meta, dict) else {}
                
        with transaction.atomic():
            # Check if an order already exists for this payment reference (idempotency)
            existing_order = Order.objects.filter(
                payment_reference=reference,
                payment_method=PaymentGateway.FLUTTERWAVE.value
            ).first()
            
            if existing_order:
                # Order already created for this reference, return it
                op.success("Order already exists for this reference (retry)")
                return {
                    "success": False,
                    "error": "Order already confirmed for this payment.",
                    "order": {
                        "id": existing_order.id,
                        "order_number": existing_order.order_number,
                        "amount": str(existing_order.total),
                        "created_at": existing_order.created_at.isoformat() if existing_order.created_at else "",
                    },
                    "reference": reference,
                }
            
            cart = Cart.objects.get(id=cart_id, is_deleted=False)
            user = cart.user

            order = Order.objects.create(
                user=user,
                subtotal=cart.subtotal(),
                shipping_fee=cart.shipping_cost(),
                discount=cart.discount(),
                total=cart.total(),
                other_info=shipping_data.get("otherInfo"),
                payment_status=PaymentStatus.PENDING.name.lower(),
                payment_reference=reference,
                payment_method=PaymentGateway.FLUTTERWAVE.value,
            )


            try:
                process_paystack_order(order.id, reference, shipping_data)
                
                order.payment_status = PaymentStatus.CONFIRMED.name.lower()
                order.save(update_fields=['payment_status'])
                op.success("Order processing task queued successfully")
            except Exception as e:
                cart.locked = False
                cart.save(update_fields=['locked'])
                
                order.payment_status = PaymentStatus.FAILED.name.lower()
                order.save(update_fields=['payment_status'])
                op.fail(f"Task failed to queue: {str(e)}")
                return {"success": False, "error": f"Order processing failed: {str(e)}"}
            
        op.success("Transaction validated and order created")
        return {
            "success": True,
            "order": {
                "id": order.id,
                "order_number": order.order_number,
                "amount": str(order.total),
                "created_at": order.created_at.isoformat() if order.created_at else "",
            },
            "reference": reference,
        }
        
    except Exception as e:
        op.fail(f"Flutterwave validation error: {str(e)}")
        return {"success": False, "error": str(e)}
