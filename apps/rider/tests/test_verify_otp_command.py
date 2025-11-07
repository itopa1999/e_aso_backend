# File: apps/rider/tests/test_verify_otp_command.py

import pytest
from http import HTTPStatus
from django.utils import timezone
from apps.aso.models import Order, ShippingAddress
from apps.rider.BLL.Commands.VerifyOtp import VerifyOtpCommand
from apps.users.models import User, UserVerification
from utils.base_result import BaseResultWithData


@pytest.mark.django_db
class TestVerifyOtpCommand:

    @pytest.fixture
    def user(self):
        return User.objects.create(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            password="securepassword"
        )

    @pytest.fixture
    def order(self, user):
        now = timezone.now()
        order = Order.objects.create(
            user=user,
            order_number="ORD123",
            total=5000,
            created_at=now,
            subtotal=4500,
            shipping_fee=500,
            is_deleted=False
        )
        # Properly create a ShippingAddress instance
        ShippingAddress.objects.create(
            order=order,
            first_name="Alice",
            last_name="Smith",
            address="123 Main St",
            apartment="",
            city="Lagos",
            state="Lagos",
            phone="08012345678",
            alt_phone=""
        )
        return order

    @pytest.fixture
    def verification(self, user):
        return UserVerification.objects.create(
            user=user,
            token="123456",
            created_at=timezone.now(),
            is_verified=False,
            is_deleted=False
        )

    def mock_request(self):
        # Dummy request with build_absolute_uri
        class DummyRequest:
            def build_absolute_uri(self, x):
                return f"http://testserver{x}"
        return DummyRequest()

    def test_order_not_found(self):
        result = VerifyOtpCommand.execute(self.mock_request(), "NONEXISTENT", "123456")
        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert result.message == "Order not found"

    def test_no_otp_found(self, order):
        result = VerifyOtpCommand.execute(self.mock_request(), order.order_number, "123456")
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert result.message == "No OTP found for this user"

    def test_otp_expired(self, order, verification):
        verification.created_at = timezone.now() - timezone.timedelta(minutes=11)
        verification.save()
        result = VerifyOtpCommand.execute(self.mock_request(), order.order_number, verification.token)
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert result.message == "OTP expired"

    def test_invalid_otp(self, order, verification):
        result = VerifyOtpCommand.execute(self.mock_request(), order.order_number, "999999")
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert result.message == "Invalid OTP"

    def test_successful_verification(self, order, verification):
        result = VerifyOtpCommand.execute(self.mock_request(), order.order_number, verification.token)
        verification.refresh_from_db()
        assert result.status_code == HTTPStatus.OK
        assert result.message == "OTP verified successfully"
        assert verification.is_verified is True
        assert "order_details" in result.data
        assert result.data["order_details"]["order_id"] == order.order_number
