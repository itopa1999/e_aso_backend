import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
from http import HTTPStatus
from apps.aso.BBL.Commands.Cart.PlaceOrder import PlaceOrderCommand
from apps.aso.models import Cart
from apps.users.models import User

@pytest.mark.django_db
class TestPlaceOrderCommand:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = User.objects.create_user(email="test@test.com", password="pass123")
        self.cart = Cart.objects.create(user=self.user, is_deleted=False)
        self.shipping_data = {"total": str(self.cart.total()) if hasattr(self.cart, "total") else "1000"}

    def test_cart_does_not_exist(self):
        """Should return BAD_REQUEST if user has no cart"""
        user_without_cart = User.objects.create_user(email="nocart@test.com", password="pass123")
        request = MagicMock(user=user_without_cart)
        result = PlaceOrderCommand.execute(request, self.shipping_data)
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert result.message == "Cart not found."

    def test_total_mismatch(self):
        """Should return BAD_REQUEST if total does not match"""
        request = MagicMock(user=self.user)
        bad_shipping_data = {"total": str(Decimal("999999"))}
        result = PlaceOrderCommand.execute(request, bad_shipping_data)
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "Total mismatch" in result.message

    @patch("apps.aso.BBL.Commands.Cart.PlaceOrder.initiate")
    def test_successful_order_initialization(self, mock_initiate):
        """Should return OK with checkout link if everything is valid"""
        checkout_url = "https://checkout.paystack.com/fake-link"
        mock_initiate.return_value = checkout_url
        request = MagicMock(user=self.user)
        result = PlaceOrderCommand.execute(request, self.shipping_data)
        assert result.status_code == HTTPStatus.OK
        assert result.data["checkout_url"] == checkout_url
        assert "Order initialized successfully" in result.message

    @patch("apps.aso.BBL.Commands.Cart.PlaceOrder.initiate")
    def test_payment_initialization_failure(self, mock_initiate):
        """Should return INTERNAL_SERVER_ERROR if payment fails"""
        mock_initiate.return_value = None
        request = MagicMock(user=self.user)
        result = PlaceOrderCommand.execute(request, self.shipping_data)
        assert result.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert "Payment initialization failed" in result.message
