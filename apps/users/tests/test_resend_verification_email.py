import pytest
from unittest.mock import patch
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.http import HttpRequest
from http import HTTPStatus

from apps.users.BBL.Commands.ResendVerificationEmail import ResendVerificationEmailCommand
from apps.users.models import User, UserVerification


@pytest.mark.django_db
class TestResendVerificationEmailCommand:
    def setup_method(self):
        self.request = HttpRequest()
        self.request.build_absolute_uri = lambda path: f"http://testserver{path}"

        self.active_user = User.objects.create(
            first_name="Lucky",
            email="active@test.com",
            is_active=True
        )

        self.inactive_user = User.objects.create(
            first_name="Peace",
            email="inactive@test.com",
            is_active=False
        )

    # 🔹 1. Magic login flow for active users
    @patch("apps.users.BBL.Commands.ResendVerificationEmail.send_custom_email")
    @patch("apps.users.BBL.Commands.ResendVerificationEmail.generate_magic_token", return_value="magic123")
    def test_magic_login_flow_success(self, mock_token, mock_email):
        data = {"email": self.active_user.email, "is_login": True}

        result = ResendVerificationEmailCommand.Execute(data, self.request)

        assert result.status_code == HTTPStatus.OK
        assert "magic login link" in result.message.lower()
        mock_token.assert_called_once_with(self.active_user.email)
        mock_email.assert_called_once()
        assert "magic123" in mock_email.call_args[1]["message"]

    # 🔹 2. Magic login with inactive user (should fail)
    def test_magic_login_with_inactive_user_fails(self):
        data = {"email": self.inactive_user.email, "is_login": True}
        result = ResendVerificationEmailCommand.Execute(data, self.request)

        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "inactive" in result.message.lower()

    # 🔹 3. Email verification flow for inactive user
    @patch("apps.users.BBL.Commands.ResendVerificationEmail.send_custom_email")
    def test_resend_verification_email_flow_success(self, mock_email):
        data = {"email": self.inactive_user.email, "is_login": False}

        result = ResendVerificationEmailCommand.Execute(data, self.request)

        assert result.status_code == HTTPStatus.OK
        assert "verification email" in result.message.lower()
        verification = UserVerification.objects.get(user=self.inactive_user)
        assert len(verification.token) == 6
        mock_email.assert_called_once()

    # 🔹 4. Email verification for already active user
    def test_resend_verification_email_already_verified_fails(self):
        data = {"email": self.active_user.email, "is_login": False}
        result = ResendVerificationEmailCommand.Execute(data, self.request)

        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "already verified" in result.message.lower()

    # 🔹 5. Non-existent email should return 404
    def test_resend_verification_email_user_not_found(self):
        data = {"email": "notfound@test.com", "is_login": False}
        result = ResendVerificationEmailCommand.Execute(data, self.request)

        assert result.status_code == HTTPStatus.NOT_FOUND
        assert "does not" in result.message.lower()
