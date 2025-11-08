import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.aso.models import Cart, CartItem, Product, Order
from apps.aso.paystack import initiate, validate

User = get_user_model()

@pytest.mark.django_db
class TestPaystack:

    def setup_method(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass123")
        self.product = Product.objects.create(title="Test Product", current_price=1000)
        self.cart = Cart.objects.create(user=self.user, is_deleted=False)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2, is_deleted=False)
        self.request = MagicMock()
        self.request.user = self.user
        self.request.build_absolute_uri.return_value = "http://testserver/callback/"

    @patch("apps.aso.paystack.req.post")
    def test_initiate_success(self, mock_post):
        """✅ Should return Paystack authorization_url when API succeeds"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {"authorization_url": "http://paystack.com/checkout"}
        }

        url = initiate(self.request, self.user, self.cart.id, {"total": 2000})
        assert url == "http://paystack.com/checkout"
        mock_post.assert_called_once()

    @patch("apps.aso.paystack.req.post")
    def test_initiate_failure(self, mock_post):
        """❌ Should return None when API fails"""
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {}

        url = initiate(self.request, self.user, self.cart.id, {"total": 2000})
        assert url is None

    @patch("apps.aso.paystack.req.get")
    def test_validate_success(self, mock_get):
        """✅ Should create order and return success when Paystack transaction is valid"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": {
                "status": "success",
                "metadata": {
                    "cart_id": self.cart.id,
                    "data": {"first_name": "John",
                             "last_name": "Doe",
                             "address": "123 Street", 
                             "city": "Lagos", 
                             "state": "LA", 
                             "phone": "08012345678",
                             "alt_phone": "08087654321"
                             }
                }
            }
        }

        result = validate("ref_12345")
        assert result["success"] is True
        assert "order" in result
        assert Order.objects.filter(user=self.user).exists()
        assert not Cart.objects.filter(id=self.cart.id).exists()  # cart deleted after validation

    @patch("apps.aso.paystack.req.get")
    def test_validate_failed_transaction(self, mock_get):
        """❌ Should return failure if transaction status is not success"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": {"status": "failed"}}

        result = validate("ref_12345")
        assert result["success"] is False
        assert "error" in result

    @patch("apps.aso.paystack.req.get")
    def test_validate_cart_does_not_exist(self, mock_get):
        """❌ Should handle Cart.DoesNotExist"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": {"status": "success", "metadata": {"cart_id": 9999, "data": {}}}
        }

        result = validate("ref_12345")
        assert result["success"] is False
        assert result["error"] == "Cart not found or already processed."
