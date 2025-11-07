# File: test_login_command.py

import pytest
from http import HTTPStatus
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from apps.administrator.BLL.Commands.Login import LoginCommand
from apps.administrator.BLL.Commands.vierifyToken import AdminVerifyOtpCommand
from utils.base_result import BaseResultWithData

User = get_user_model()

@pytest.mark.django_db
class TestLoginCommand:
    @pytest.fixture
    def admin_user(self):
        """Creates a test admin user"""
        user = User.objects.create_user(
            email="admin@example.com",
            password="securepassword",
            first_name="Admin",
            is_active=True
        )
        return user

    def test_login_successful(self, admin_user):
        """Should return tokens and user info for valid OTP and credentials"""
        with patch.object(AdminVerifyOtpCommand, "execute") as mock_otp, \
             patch("django.contrib.auth.authenticate") as mock_auth:

            mock_otp.return_value = MagicMock(status_code=200, message="Token verified")
            mock_auth.return_value = admin_user

            result = LoginCommand.execute("123456", admin_user.email, "securepassword")

        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.OK
        assert result.data["email"] == admin_user.email
        assert "access_token" in result.data
        assert "refresh_token" in result.data
        assert result.message == "Login successful."

    def test_login_fails_invalid_otp(self, admin_user):
        """Should fail if OTP verification fails"""
        with patch.object(AdminVerifyOtpCommand, "execute") as mock_otp:
            mock_otp.return_value = MagicMock(status_code=400, message="Invalid token")

            result = LoginCommand.execute("wrongtoken", admin_user.email, "securepassword")

        assert result.status_code == 400
        assert result.data is None
        assert "Invalid token" in result.message

    def test_login_fails_wrong_password(self, admin_user):
        """Should fail if credentials are wrong"""
        with patch.object(AdminVerifyOtpCommand, "execute") as mock_otp, \
             patch("django.contrib.auth.authenticate") as mock_auth:

            mock_otp.return_value = MagicMock(status_code=200, message="Token verified")
            mock_auth.return_value = None

            result = LoginCommand.execute("123456", admin_user.email, "wrongpassword")

        assert result.status_code == HTTPStatus.UNAUTHORIZED
        assert result.data is None
        assert "Invalid email or password" in result.message

