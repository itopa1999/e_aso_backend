import pytest
from unittest.mock import patch
from django.http import HttpRequest
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from http import HTTPStatus

from apps.users.BBL.Commands.SendMagicLink import SendMagicLinkCommand
from apps.users.models import User, UserVerification


@pytest.mark.django_db
class TestSendMagicLinkCommand:
    def setup_method(self):
        # Mock request and build_absolute_uri behavior
        self.request = HttpRequest()
        self.request.build_absolute_uri = lambda path: f"http://testserver{path}"

        # Create test users
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

    # 🆕 1. New user registration flow (no existing user)
    @patch("apps.users.BBL.Commands.SendMagicLink.send_custom_email")
    @patch("apps.users.BBL.Commands.SendMagicLink.RegUserSerializer")
    def test_new_user_registration_sends_verification_email(self, mock_serializer, mock_send_email):
        mock_user = User(id=10, first_name="NewUser", email="new@test.com", is_active=False)
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.save.return_value = mock_user

        validated_data = {"email": "new@test.com", "first_name": "NewUser"}

        result = SendMagicLinkCommand.Execute(self.request, validated_data)

        assert result.status_code == HTTPStatus.CREATED
        assert "verification email" in result.message.lower()
        mock_send_email.assert_called_once()
        assert result.data["email"] == "new@test.com"
        mock_serializer.assert_called_once()

    # 🚫 2. Existing inactive user (should not send magic link)
    def test_existing_inactive_user_fails_with_bad_request(self):
        validated_data = {"email": self.inactive_user.email}
        result = SendMagicLinkCommand.Execute(self.request, validated_data)

        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "inactive" in result.message.lower()

    # ✅ 3. Existing active user (sends magic login link)
    @patch("apps.users.BBL.Commands.SendMagicLink.send_custom_email")
    @patch("apps.users.BBL.Commands.SendMagicLink.generate_magic_token", return_value="magic123")
    def test_existing_active_user_magic_link_success(self, mock_token, mock_email):
        validated_data = {"email": self.active_user.email}

        result = SendMagicLinkCommand.Execute(self.request, validated_data)

        assert result.status_code == HTTPStatus.OK
        assert "magic login link" in result.message.lower()
        assert result.data["email"] == self.active_user.email

        mock_token.assert_called_once_with(self.active_user.email)
        mock_email.assert_called_once()
        assert "magic123" in mock_email.call_args[1]["message"]
