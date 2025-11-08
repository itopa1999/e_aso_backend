import pytest
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from apps.users.BBL.Commands.VerifyEmail import VerifyEmailCommand
from apps.users.models import User, UserVerification
from unittest.mock import patch
from datetime import timedelta
from django.utils import timezone


@pytest.mark.django_db
class TestVerifyEmailCommand:
    def setup_method(self):
        self.user = User.objects.create(
            first_name="Lucky",
            email="lucky@test.com",
            is_active=False,
        )
        self.verification = UserVerification.objects.create(
            user=self.user,
            token="123456",
            is_verified=False,
        )

        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))
        self.token = self.verification.token
        self.url_email = self.user.email

    def test_successful_verification(self, settings):
        """✅ Should verify user and redirect to success page with tokens"""
        response = VerifyEmailCommand.Execute(self.uidb64, self.token, self.url_email)

        self.user.refresh_from_db()
        self.verification.refresh_from_db()

        assert self.user.is_active is True
        assert self.verification.is_verified is True
        assert response.status_code == 302
        assert response.url.startswith(f"{settings.BASE_URL}/index.html?")

    def test_expired_token_redirects_to_failed_page(self):
        """❌ Expired token should redirect to failure page"""
        self.verification.created_at = timezone.now() - timedelta(minutes=1)
        self.verification.save()

        with patch.object(UserVerification, 'is_token_expired', return_value=True):
            response = VerifyEmailCommand.Execute(self.uidb64, self.token, self.url_email)

        assert response.status_code == 302
        assert response.url.startswith(f"{settings.BASE_URL}/verified-email-failed.html")

    def test_already_verified_redirects_to_failed_page(self):
        """❌ Already verified token should redirect to failure page"""
        self.verification.is_verified = True
        self.verification.save()

        response = VerifyEmailCommand.Execute(self.uidb64, self.token, self.url_email)
        assert response.status_code == 302
        assert response.url.startswith(f"{settings.BASE_URL}/verified-email-failed.html")

    def test_invalid_token_or_uid_raises_404(self):
        """❌ Invalid UID or token should raise 404"""
        invalid_uid = urlsafe_base64_encode(force_bytes(99999))  # nonexistent user
        invalid_token = "wrongtoken"

        with pytest.raises(Exception):  # get_object_or_404 should raise
            VerifyEmailCommand.Execute(invalid_uid, invalid_token, self.url_email)
