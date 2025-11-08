import pytest
from http import HTTPStatus
from apps.aso.BBL.Commands.Cart.MoveAllToCart import MoveAllToCartCommand
from apps.aso.models import WatchList, Product, Cart, CartItem


@pytest.mark.django_db
class TestMoveAllToCartCommand:
    def setup_method(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            email="moveall@test.com",
            password="pass123"
        )

        # Create sample products
        self.product1 = Product.objects.create(title="Fabric A", current_price=1000, rating=4.0)
        self.product2 = Product.objects.create(title="Fabric B", current_price=1500, rating=4.3)

    def test_moves_all_items_to_cart(self):
        """✅ Should move all watchlist items to cart"""
        WatchList.objects.create(user=self.user, product=self.product1, is_deleted=False)
        WatchList.objects.create(user=self.user, product=self.product2, is_deleted=False)

        response = MoveAllToCartCommand.execute(self.user)

        assert response.status_code == HTTPStatus.OK
        assert response.data["items_added"] == 2
        assert "2 items moved" in response.message

        cart = Cart.objects.get(user=self.user, is_deleted=False)
        cart_items = CartItem.objects.filter(cart=cart, is_deleted=False)
        assert cart_items.count() == 2
        assert {ci.product for ci in cart_items} == {self.product1, self.product2}

    def test_no_items_in_watchlist(self):
        """🧩 Should handle empty watchlist gracefully"""
        response = MoveAllToCartCommand.execute(self.user)

        assert response.status_code == HTTPStatus.OK
        assert response.data["items_added"] == 0
        assert "no items" in response.message.lower()

    def test_does_not_duplicate_existing_cart_items(self):
        """🚫 Should not duplicate cart items already present"""
        # Create both watchlist and cart items
        WatchList.objects.create(user=self.user, product=self.product1, is_deleted=False)
        cart = Cart.objects.create(user=self.user, is_deleted=False)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=1, is_deleted=False)

        response = MoveAllToCartCommand.execute(self.user)

        assert response.status_code == HTTPStatus.OK
        assert response.data["items_added"] == 0  # already exists
        assert "0 items moved" in response.message

        assert CartItem.objects.filter(cart=cart, product=self.product1).count() == 1
