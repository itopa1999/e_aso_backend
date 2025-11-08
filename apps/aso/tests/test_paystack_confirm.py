# apps/aso/tests/test_paystack_confirm_query.py
import pytest
from unittest.mock import patch, MagicMock
from http import HTTPStatus
from django.conf import settings

from apps.aso.BBL.Queries.Cart.PaystackConfirm import PaystackConfirmQuery

@pytest.mark.django_db
class TestPaystackConfirmQuery:

    @patch("apps.aso.BBL.Queries.Cart.PaystackConfirm.validate")
    @patch("apps.aso.BBL.Queries.Cart.PaystackConfirm.send_mail")
    @patch("apps.aso.BBL.Queries.Cart.PaystackConfirm.redirect")
    def test_execute_successful_payment(self, mock_redirect, mock_send_mail, mock_validate):
        """✅ Should redirect to order-success.html and send email on success"""
        reference = "ref_12345"
        mock_validate.return_value = {
            "success": True,
            "order": {
                "id": 1,
                "order_number": "ORD123",
                "amount": 2500,
                "created_at": "2025-11-07T10:00:00"
            }
        }
        mock_redirect.side_effect = lambda url: url

        redirect_url = PaystackConfirmQuery.execute(reference)

        assert "/order-success.html" in redirect_url
        assert "order_id=1" in redirect_url
        mock_send_mail.assert_called_once()
        mock_validate.assert_called_once_with(reference)

    @patch("apps.aso.BBL.Queries.Cart.PaystackConfirm.validate")
    @patch("apps.aso.BBL.Queries.Cart.PaystackConfirm.redirect")
    def test_execute_failed_payment(self, mock_redirect, mock_validate):
        """✅ Should redirect to order-failed.html if validation fails"""
        reference = "ref_54321"
        mock_validate.return_value = {"success": False, "error": "Insufficient funds"}
        mock_redirect.side_effect = lambda url: url

        redirect_url = PaystackConfirmQuery.execute(reference)

        assert "/order-failed.html" in redirect_url
        assert "error=Insufficient funds" in redirect_url
        mock_validate.assert_called_once_with(reference)

    def test_execute_no_reference(self):
        """❌ Should return BAD_REQUEST if no reference is provided"""
        result = PaystackConfirmQuery.execute(None)
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert result.message == "No reference provided"
