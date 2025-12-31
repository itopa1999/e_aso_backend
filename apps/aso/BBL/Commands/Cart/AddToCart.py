from http import HTTPStatus
import json
import logging
from django.db import transaction
from apps.aso.models import Product, Cart, CartItem
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger


class AddToCartCommand:
    @staticmethod
    def execute(user, product_id, quantity=None, desc=None):
        op = OperationLogger(
            "AddToCartCommand",
            user=user.id if user else "Anonymous",
            product_id=product_id,
            quantity=quantity
        )
        op.start()
        
        try:
            product = Product.objects.get(id=product_id, is_deleted=False)
        except Product.DoesNotExist as e:
            op.fail("Product not found", e)
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.NOT_FOUND,
                message="Product not found"
            )

        try:
            desc_data = json.loads(desc) if isinstance(desc, str) else desc
        except json.JSONDecodeError as e:
            op.fail("Invalid desc format", e)
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message="Invalid desc format"
            )

        with transaction.atomic():
            cart, _ = Cart.objects.get_or_create(user=user, is_deleted=False)
            items_added = 0

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={"quantity": int(quantity) if quantity else 1, "desc": desc_data or {}},
                is_deleted=False
            )

            if not created:
                if quantity:
                    cart_item.quantity = int(quantity)
                if desc_data:
                    cart_item.desc = desc_data
                cart_item.save()
            else:
                items_added += 1

        op.success("Item added to cart")
        return BaseResultWithData(
            data={"items_added": items_added},
            status_code=HTTPStatus.OK,
            message="Item added to cart"
        )
