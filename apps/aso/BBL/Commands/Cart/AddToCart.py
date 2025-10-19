# apps/aso/commands/add_to_cart_command.py
from http import HTTPStatus
import json
from apps.aso.models import Product, Cart, CartItem
from utils.base_result import BaseResultWithData


class AddToCartCommand:
    @staticmethod
    def execute(user, product_id, quantity=None, desc=None):
        try:
            product = Product.objects.get(id=product_id, is_deleted=False)
        except Product.DoesNotExist:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.NOT_FOUND,
                message="Product not found"
            )

        try:
            desc_data = json.loads(desc) if isinstance(desc, str) else desc
        except json.JSONDecodeError:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message="Invalid desc format"
            )

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

        return BaseResultWithData(
            data={"items_added": items_added},
            status_code=HTTPStatus.OK,
            message="Item added to cart"
        )
