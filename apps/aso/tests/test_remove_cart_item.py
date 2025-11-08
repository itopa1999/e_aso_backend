import pytest
from unittest.mock import MagicMock
from http import HTTPStatus
from django.contrib.auth import get_user_model
from apps.aso.BBL.Commands.Cart.RemoveCartItem import RemoveCartItemCommand
from apps.aso.models import Product, Cart, CartItem


@pytest.mark.django_db
class TestRemoveCartItemCommand:
    def setup_method(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="removetest@test.com", password="password123"
        )

        self.product = Product.objects.create(title="Sneakers", current_price=25000, rating=4.8)
        self.cart = Cart.objects.create(user=self.user, is_deleted=False)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=2, is_deleted=False
        )

    def test_remove_cart_item_successfully(self):
        """✅ Should remove a cart item successfully"""
        serializer = MagicMock()
        serializer.is_valid.return_value = True
        serializer.validated_data = {"item_id": self.cart_item.id}

        result = RemoveCartItemCommand.execute(self.user, serializer)

        assert result.status_code == HTTPStatus.OK
        assert result.data["item_id"] == self.cart_item.id
        assert "removed successfully" in result.message.lower()
        # Verify item is deleted
        assert not CartItem.objects.filter(id=self.cart_item.id).exists()

    def test_invalid_serializer_returns_bad_request(self):
        """🚫 Should return BAD_REQUEST when serializer is invalid"""
        serializer = MagicMock()
        serializer.is_valid.return_value = False
        serializer.errors = {"item_id": ["This field is required."]}

        result = RemoveCartItemCommand.execute(self.user, serializer)

        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert result.data is None
        assert "item_id" in str(result.message)

    def test_cart_item_not_found_returns_not_found(self):
        """❌ Should return NOT_FOUND when item does not exist"""
        serializer = MagicMock()
        serializer.is_valid.return_value = True
        serializer.validated_data = {"item_id": 9999}

        result = RemoveCartItemCommand.execute(self.user, serializer)

        assert result.status_code == HTTPStatus.NOT_FOUND
        assert result.data is None
        assert "not found" in result.message.lower()
