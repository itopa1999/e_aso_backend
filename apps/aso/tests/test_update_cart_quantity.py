import pytest
from unittest.mock import MagicMock
from http import HTTPStatus
from django.contrib.auth import get_user_model
from apps.aso.BBL.Commands.Cart.UpdateCartQuantity import UpdateCartQuantityCommand
from apps.aso.models import Cart, CartItem, Product


@pytest.mark.django_db
class TestUpdateCartQuantityCommand:
    def setup_method(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="updatecart@test.com",
            password="pass123"
        )

        self.product = Product.objects.create(title="Aso Oke", current_price=1500, rating=4.0)
        self.cart = Cart.objects.create(user=self.user, is_deleted=False)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=2, is_deleted=False
        )

    def test_successful_update_quantity(self):
        """✅ Should update cart item quantity successfully"""
        serializer = MagicMock()
        serializer.is_valid.return_value = True
        serializer.validated_data = {
            "item_id": self.cart_item.id,
            "quantity": 5,
        }

        result = UpdateCartQuantityCommand.execute(self.user, serializer)

        self.cart_item.refresh_from_db()
        assert result.status_code == HTTPStatus.OK
        assert result.data["quantity"] == 5
        assert "updated successfully" in result.message.lower()

    def test_invalid_serializer_returns_bad_request(self):
        """🚫 Should return BAD_REQUEST if serializer invalid"""
        serializer = MagicMock()
        serializer.is_valid.return_value = False
        serializer.errors = {"quantity": ["This field is required."]}

        result = UpdateCartQuantityCommand.execute(self.user, serializer)

        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "quantity" in str(result.message)

    def test_item_not_found_returns_not_found(self):
        """❌ Should return NOT_FOUND if cart item doesn’t exist"""
        serializer = MagicMock()
        serializer.is_valid.return_value = True
        serializer.validated_data = {
            "item_id": 999,  # Nonexistent
            "quantity": 3,
        }

        result = UpdateCartQuantityCommand.execute(self.user, serializer)

        assert result.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in result.message.lower()
