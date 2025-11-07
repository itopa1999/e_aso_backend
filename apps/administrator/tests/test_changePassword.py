import pytest
from http import HTTPStatus
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import Group
from apps.users.models import User, UserVerification
from apps.administrator.BLL.Commands.vierifyToken import AdminVerifyOtpCommand
from utils.base_result import BaseResult
from utils.enum import GroupNames


@pytest.mark.django_db
class TestAdminVerifyOtpCommand:

    def setup_method(self):
        """Setup one user and verification record"""
        self.user = User.objects.create_user(
            email="admin@test.com",
            password="oldpassword123",
            is_deleted=False
        )

        admin_group, _ = Group.objects.get_or_create(name=GroupNames.ADMIN.value)
        self.user.groups.add(admin_group)
        
        self.verification = UserVerification.objects.create(
            user=self.user,
            token="123456",
            is_deleted=False
        )

    def test_user_or_verification_not_found(self):
        """Should return 400 if user or verification record not found"""
        result = AdminVerifyOtpCommand.execute("000000", "notfound@test.com")
        assert isinstance(result, BaseResult)
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "not found" in result.message

    def test_invalid_token(self):
        """Should fail when token does not match"""
        result = AdminVerifyOtpCommand.execute("999999", self.user.email)
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "Invalid token" in result.message

    def test_expired_token(self):
        """Should fail if token is expired"""
        self.verification.created_at = timezone.now() - timedelta(minutes=100)
        self.verification.save()

        # Mock is_token_expired() to simulate expiry
        def expired():
            return True
        self.verification.is_token_expired = expired

        result = AdminVerifyOtpCommand.execute("123456", self.user.email)
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "expired" in result.message

    def test_valid_token(self):
        """Should pass if token is valid"""
        result = AdminVerifyOtpCommand.execute("123456", self.user.email)
        assert result.status_code == HTTPStatus.OK
        assert "verified" in result.message
