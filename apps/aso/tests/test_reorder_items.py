import pytest
from http import HTTPStatus
from unittest.mock import patch

from apps.aso.BBL.Commands.Cart.ReorderItems import ReorderItemsCommand
from apps.aso.models import Order, Cart, CartItem, Product, OrderItem
from utils.base_result import BaseResultWithData


@pytest.mark.django_db
class TestReorderItemsCommand:

    def setup_method(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            email="tracking@test.com",
            password="pass123"
        )
        self.order = Order.objects.create(
            user=self.user,
            total=2500,
            shipping_fee=200,
            subtotal=2300,
            is_deleted=False
        )
        self.product = Product.objects.create(
            title="Aso Oke Fabric",
           current_price=1200, rating=4.5
        )
        # Create an order item for the product
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price = self.product.original_price,
        )

    @patch("apps.aso.BBL.Commands.Cart.ReorderItems.OperationLogger")
    def test_missing_order_id_returns_bad_request(self, mock_logger):
        """❌ Should return BAD_REQUEST when order_id is missing"""
        result = ReorderItemsCommand.execute(self.user, None)

        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "required" in result.message.lower()

    @patch("apps.aso.BBL.Commands.Cart.ReorderItems.OperationLogger")
    def test_order_not_found_returns_not_found(self, mock_logger):
        """❌ Should return NOT_FOUND when order does not exist"""
        result = ReorderItemsCommand.execute(self.user, 99999)

        assert result.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in result.message.lower()

    @patch("apps.aso.BBL.Commands.Cart.ReorderItems.OperationLogger")
    def test_successful_reorder_creates_cart_items(self, mock_logger):
        """✅ Should create cart items from order items"""
        result = ReorderItemsCommand.execute(self.user, self.order.id)

        assert result.status_code == HTTPStatus.OK
        assert "reordered" in result.message.lower() or "items" in result.message.lower()

        cart = Cart.objects.get(user=self.user)
        cart_items = CartItem.objects.filter(cart=cart)

        assert cart_items.count() == 1
        item = cart_items.first()
        assert item.product == self.product
        assert item.quantity == 2

    @patch("apps.aso.BBL.Commands.Cart.ReorderItems.OperationLogger")
    def test_reorder_does_not_duplicate_existing_cart_items(self, mock_logger):
        """⚙️ Should not duplicate cart items if already present"""
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        result = ReorderItemsCommand.execute(self.user, self.order.id)

        assert result.status_code == HTTPStatus.OK

        # Only 1 item should exist (no duplicates)
        assert CartItem.objects.filter(cart=cart, product=self.product).count() == 1
