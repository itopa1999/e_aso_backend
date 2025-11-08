import pytest
from unittest.mock import patch, MagicMock
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.BBL.Commands.MagicLogin import MagicLoginCommand
from apps.users.models import User


@pytest.mark.django_db
class TestMagicLoginCommand:
    def setup_method(self):
        self.user = User.objects.create(
            first_name="Lucky",
            email="lucky@test.com",
            is_active=True,
        )

        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))
        self.valid_token = "valid_token_123"
        self.url_email = self.user.email

    # ✅ Successful login with valid token
    @patch("apps.users.BBL.Commands.MagicLogin.validate_magic_token")
    @patch("apps.users.BBL.Commands.MagicLogin.RefreshToken.for_user")
    def test_successful_magic_login_redirects_to_index(self, mock_refresh_cls, mock_validate_token):
        mock_validate_token.return_value = self.user.email

        mock_refresh = MagicMock()
        mock_refresh_cls.for_user.return_value = mock_refresh
        mock_refresh.__str__.return_value = "refresh123"
        mock_refresh.access_token = MagicMock()
        mock_refresh.access_token.__str__.return_value = "access123"

        response = MagicLoginCommand.Execute(self.uidb64, self.valid_token, self.url_email)

        # Assertions
        assert response.status_code == 302
        assert response.url.startswith(f"{settings.BASE_URL}/index.html?")
        mock_validate_token.assert_called_once_with(self.valid_token)

    # ❌ Invalid token - validation fails
    @patch("apps.users.BBL.Commands.MagicLogin.validate_magic_token")
    def test_invalid_token_redirects_to_failed_page(self, mock_validate_token):
        mock_validate_token.return_value = None  # token invalid

        response = MagicLoginCommand.Execute(self.uidb64, "invalid_token", self.url_email)

        assert response.status_code == 302
        assert response.url.startswith(f"{settings.BASE_URL}/verified-email-failed.html")
        assert "is_login=true" in response.url

    # ❌ Token valid but belongs to different email
    @patch("apps.users.BBL.Commands.MagicLogin.validate_magic_token")
    def test_token_email_mismatch_redirects_to_failed_page(self, mock_validate_token):
        mock_validate_token.return_value = "wrongemail@test.com"

        response = MagicLoginCommand.Execute(self.uidb64, "valid_token", self.url_email)

        assert response.status_code == 302
        assert response.url.startswith(f"{settings.BASE_URL}/verified-email-failed.html")
        assert "is_login=true" in response.url
