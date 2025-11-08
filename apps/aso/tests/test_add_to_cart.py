import pytest
from http import HTTPStatus
from apps.aso.BBL.Commands.Cart.AddToCart import AddToCartCommand
from apps.aso.models import Product, Cart, CartItem


@pytest.mark.django_db
class TestAddToCartCommand:
    def setup_method(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            email="cart@test.com",
            password="pass123"
        )
        self.product = Product.objects.create(
            title="Aso Oke Fabric",
            current_price=1200,
            rating=4.5
        )

    def test_adds_new_item_to_cart(self):
        """✅ Should add a new product to user's cart"""
        response = AddToCartCommand.execute(
            user=self.user,
            product_id=self.product.id,
            quantity=2,
            desc={"color": "blue"}
        )

        assert response.status_code == HTTPStatus.OK
        assert response.data["items_added"] == 1
        assert "Item added" in response.message

        cart = Cart.objects.get(user=self.user)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        assert cart_item.quantity == 2
        assert cart_item.desc == {"color": "blue"}

    def test_updates_existing_cart_item(self):
        """🧩 Should update quantity/desc if item already exists"""
        cart = Cart.objects.create(user=self.user, is_deleted=False)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1, desc={"size": "M"}, is_deleted=False)

        response = AddToCartCommand.execute(
            user=self.user,
            product_id=self.product.id,
            quantity=5,
            desc={"color": "red"}
        )

        assert response.status_code == HTTPStatus.OK
        assert response.data["items_added"] == 0  # not a new item
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        assert cart_item.quantity == 5
        assert cart_item.desc == {"color": "red"}

    def test_invalid_product_returns_404(self):
        """🚫 Should return 404 for invalid product"""
        response = AddToCartCommand.execute(
            user=self.user,
            product_id=9999
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in response.message.lower()

    def test_invalid_desc_format(self):
        """🚫 Should return 400 if desc JSON is invalid"""
        invalid_json = "{invalid: json}"
        response = AddToCartCommand.execute(
            user=self.user,
            product_id=self.product.id,
            desc=invalid_json
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "invalid desc" in response.message.lower()

    def test_defaults_to_quantity_1_and_empty_desc(self):
        """🔢 Should default to quantity=1 and desc={} when not provided"""
        response = AddToCartCommand.execute(
            user=self.user,
            product_id=self.product.id
        )
        assert response.status_code == HTTPStatus.OK

        cart_item = CartItem.objects.get(cart__user=self.user, product=self.product)
        assert cart_item.quantity == 1
        assert cart_item.desc == {}
