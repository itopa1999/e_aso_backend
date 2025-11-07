# File: apps/administrator/tests/test_send_otp_command.py

import pytest
from unittest.mock import patch
from http import HTTPStatus
from django.utils import timezone
from apps.aso.models import Order, OrderTracking
from apps.rider.BLL.Commands.SendOtp import SendOtpCommand
from apps.users.models import User, UserVerification
from utils.base_result import BaseResultWithData


@pytest.mark.django_db
class TestSendOtpCommand:
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
        return Order.objects.create(
            user=user,
            order_number="ORD123",
            total=100,
            created_at=now,
            subtotal=300,
            shipping_fee=30,
            is_deleted=False
        )

    def test_order_not_found(self):
        result = SendOtpCommand.execute("NONEXISTENT")
        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert result.message == "Order not found"

    def test_order_already_delivered_or_cancelled(self, order):
        now = timezone.now()
        OrderTracking.objects.create(order=order, status="placed", date=now)
        OrderTracking.objects.create(order=order, status="processing", date=now)
        OrderTracking.objects.create(order=order, status="shipped", date=now)
        OrderTracking.objects.create(order=order, status="in_transit", date=now)
        OrderTracking.objects.create(order=order, status="cancelled", date=now)
        result = SendOtpCommand.execute(order.order_number)
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "OTP not required" in result.message

    def test_order_not_in_transit(self, order):
        # No 'in_transit' tracking
        now = timezone.now()
        OrderTracking.objects.create(order=order, status="placed", date=now)
        result = SendOtpCommand.execute(order.order_number)
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "OTP cannot be sent" in result.message

    @patch("apps.rider.BLL.Commands.SendOtp.send_custom_email")
    def test_otp_sent_successfully(self, mock_send_email, order):
        now = timezone.now()
        OrderTracking.objects.create(order=order, status="placed", date=now)
        OrderTracking.objects.create(order=order, status="processing", date=now)
        OrderTracking.objects.create(order=order, status="shipped", date=now)
        OrderTracking.objects.create(order=order, status="in_transit", date=now)

        result = SendOtpCommand.execute(order.order_number)

        assert result.status_code == HTTPStatus.OK
        assert "OTP sent" in result.message

        verification = UserVerification.objects.get(user=order.user)
        assert verification.token is not None
        assert verification.is_verified is False

        # Ensure email was sent
        mock_send_email.assert_called_once()
        args, kwargs = mock_send_email.call_args
        assert "Your OTP is:" in kwargs["message"]
        assert kwargs["recipient_email"] == order.user.email
