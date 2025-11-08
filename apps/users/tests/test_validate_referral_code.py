import pytest
from unittest.mock import patch, MagicMock
from http import HTTPStatus
from apps.users.BBL.Commands.ValidateReferralCode import ValidateReferralCodeCommand
from apps.users.models import Referral, User
from utils.base_result import BaseResult


@pytest.mark.django_db
class TestValidateReferralCodeCommand:

    @patch("apps.users.BBL.Commands.ValidateReferralCode.is_feature_enabled")
    def test_referral_feature_disabled(self, mock_feature):
        mock_feature.return_value = False
        user = MagicMock()

        result = ValidateReferralCodeCommand.execute(user, "ABC123")

        assert isinstance(result, BaseResult)
        assert result.status_code == 400
        assert "disabled" in result.message.lower()
        mock_feature.assert_called_once()

    @patch("apps.users.BBL.Commands.ValidateReferralCode.is_feature_enabled", return_value=True)
    def test_invalid_referral_code(self, mock_feature):
        user = MagicMock()

        with patch("apps.users.BBL.Commands.ValidateReferralCode.User.objects.get") as mock_get:
            mock_get.side_effect = User.DoesNotExist

            result = ValidateReferralCodeCommand.execute(user, "INVALIDCODE")

        assert result.status_code == 400
        assert "invalid referral code" in result.message.lower()
        mock_get.assert_called_once_with(referral_code="INVALIDCODE")

    @patch("apps.users.BBL.Commands.ValidateReferralCode.is_feature_enabled", return_value=True)
    def test_user_uses_own_referral_code(self, mock_feature):
        user = MagicMock()
        user.id = 1
        referrer = MagicMock()
        referrer.id = 1

        with patch("apps.users.BBL.Commands.ValidateReferralCode.User.objects.get", return_value=referrer):
            result = ValidateReferralCodeCommand.execute(user, "SELF123")

        assert result.status_code == 400
        assert "own referral code" in result.message.lower()

    @patch("apps.users.BBL.Commands.ValidateReferralCode.is_feature_enabled", return_value=True)
    def test_user_already_referred(self, mock_feature):
        user = MagicMock()
        user.id = 2
        user.referral_used = True
        referrer = MagicMock()
        referrer.id = 1

        with patch("apps.users.BBL.Commands.ValidateReferralCode.User.objects.get", return_value=referrer):
            result = ValidateReferralCodeCommand.execute(user, "USED123")

        assert result.status_code == 400
        assert "already referred" in result.message.lower()

    @patch("apps.users.BBL.Commands.ValidateReferralCode.is_feature_enabled", return_value=True)
    def test_successful_referral(self, mock_feature, django_user_model):
        referrer = django_user_model.objects.create(email="ref@test.com", referral_code="REF123")
        user = django_user_model.objects.create(email="new@test.com", referral_used=False)

        with patch("apps.users.BBL.Commands.ValidateReferralCode.User.objects.get", return_value=referrer), \
             patch("apps.users.BBL.Commands.ValidateReferralCode.Referral.objects.create") as mock_referral:

            result = ValidateReferralCodeCommand.execute(user, "REF123")

        # Assertions
        assert isinstance(result, BaseResult)
        assert result.status_code == HTTPStatus.OK
        assert "applied successfully" in result.message.lower()
        mock_referral.assert_called_once_with(referrer=referrer, referee=user, successful=True)
