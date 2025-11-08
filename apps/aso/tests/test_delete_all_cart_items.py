import pytest
from http import HTTPStatus
from django.contrib.auth import get_user_model
from apps.aso.BBL.Commands.Cart.DeleteAllCartsItems import DeleteAllCartItemsCommand
from apps.aso.models import Cart, CartItem, Product


@pytest.mark.django_db
class TestDeleteAllCartItemsCommand:
    def setup_method(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="deletecart@test.com",
            password="password123"
        )

        self.cart = Cart.objects.create(user=self.user, is_deleted=False)
        self.product1 = Product.objects.create(title="Product 1", current_price=100)
        self.product2 = Product.objects.create(title="Product 2", current_price=200)

        self.cart_item1 = CartItem.objects.create(cart=self.cart, product=self.product1, quantity=1, is_deleted=False)
        self.cart_item2 = CartItem.objects.create(cart=self.cart, product=self.product2, quantity=2, is_deleted=False)

    def test_delete_all_cart_items_success(self):
        """✅ Should delete all items and return success"""
        result = DeleteAllCartItemsCommand.execute(self.user)

        assert result.status_code == HTTPStatus.OK
        assert "removed" in result.message.lower()
        assert CartItem.objects.filter(cart=self.cart, is_deleted=False).count() == 0

    def test_delete_all_cart_items_when_empty(self):
        """❌ Should return BAD_REQUEST if cart has no items"""
        # Delete all items first
        CartItem.objects.filter(cart=self.cart).delete()

        result = DeleteAllCartItemsCommand.execute(self.user)

        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "already empty" in result.message.lower()
