import pytest
from unittest.mock import MagicMock
from http import HTTPStatus
from django.contrib.auth import get_user_model
from apps.aso.BBL.Commands.Cart.UpdateCartDesc import UpdateCartDescCommand
from apps.aso.models import Cart, CartItem, Product


@pytest.mark.django_db
class TestUpdateCartDescCommand:
    def setup_method(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="descupdate@test.com", password="password123"
        )

        self.product = Product.objects.create(title="Adire Fabric", current_price=3000, rating=4.7)
        self.cart = Cart.objects.create(user=self.user, is_deleted=False)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=2, desc="Old description", is_deleted=False
        )

    def test_successful_update_description(self):
        """✅ Should update cart item description successfully"""
        serializer = MagicMock()
        serializer.is_valid.return_value = True
        serializer.validated_data = {
            "item_id": self.cart_item.id,
            "desc": "Updated item description"
        }

        result = UpdateCartDescCommand.execute(self.user, serializer)

        self.cart_item.refresh_from_db()
        assert result.status_code == HTTPStatus.OK
        assert result.data["desc"] == "Updated item description"
        assert "updated successfully" in result.message.lower()
        assert self.cart_item.desc == "Updated item description"

    def test_invalid_serializer_returns_bad_request(self):
        """🚫 Should return BAD_REQUEST if serializer data invalid"""
        serializer = MagicMock()
        serializer.is_valid.return_value = False
        serializer.errors = {"desc": ["This field is required."]}

        result = UpdateCartDescCommand.execute(self.user, serializer)

        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "desc" in str(result.message)
        assert result.data is None

    def test_item_not_found_returns_not_found(self):
        """❌ Should return NOT_FOUND if item does not exist"""
        serializer = MagicMock()
        serializer.is_valid.return_value = True
        serializer.validated_data = {
            "item_id": 9999,
            "desc": "New description"
        }

        result = UpdateCartDescCommand.execute(self.user, serializer)

        assert result.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in result.message.lower()
        assert result.data is None
