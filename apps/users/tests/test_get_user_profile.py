import pytest
from unittest.mock import patch, MagicMock
from http import HTTPStatus

from apps.users.BBL.Queries.GetUserProfile import GetUserProfileSummaryQuery
from utils.base_result import BaseResultWithData


@pytest.mark.django_db
class TestGetUserProfileSummaryQuery:
    def setup_method(self):
        # mock user
        self.user = MagicMock()
        self.user.id = 1
        self.user.first_name = "Lucky"
        self.user.last_name = "Salawu"
        self.user.email = "lucky@test.com"
        self.user.phone = "08012345678"
        self.user.referral_code = "REF123"
        self.user.referral_used = False
        self.user.check_referral_qualification = True
        self.user.referrals_made.filter.return_value.count.return_value = 2
        self.user.transactions.order_by.return_value = []

    # ✅ Case 1 — When cache is found
    @patch("apps.users.BBL.Queries.GetUserProfile.GlobalCache")
    def test_returns_cached_profile_summary(self, mock_cache):
        cached_data = {"data": {"email": "cached@test.com"}}
        mock_cache.get.return_value = cached_data

        result = GetUserProfileSummaryQuery.query(self.user)

        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.OK
        assert result.data == cached_data["data"]
        mock_cache.get.assert_called_once()

    # ✅ Case 2 — When no cache exists (fresh DB fetch)
    @patch("apps.users.BBL.Queries.GetUserProfile.UserOrderSummarySerializer")
    @patch("apps.users.BBL.Queries.GetUserProfile.Order")
    @patch("apps.users.BBL.Queries.GetUserProfile.GlobalCache")
    def test_returns_fresh_summary_and_sets_cache(self, mock_cache, mock_order, mock_serializer):
        mock_cache.get.return_value = None

        # Fake queryset results
        fake_orders = MagicMock()
        fake_orders.count.return_value = 5
        fake_orders.__getitem__.return_value = ["order1", "order2"]
        mock_order.objects.filter.return_value.order_by.return_value = fake_orders

        # Mock serializer
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.data = {"email": "fresh@test.com"}
        mock_serializer.return_value = mock_serializer_instance

        result = GetUserProfileSummaryQuery.query(self.user)

        # Assertions
        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.OK
        assert result.data == {"email": "fresh@test.com"}

        # Verify cache was written
        mock_cache.set.assert_called_once()
        mock_order.objects.filter.assert_called_once_with(user=self.user, is_deleted=False)

    # ✅ Case 3 — Ensure serializer receives correct structure
    @patch("apps.users.BBL.Queries.GetUserProfile.UserOrderSummarySerializer")
    @patch("apps.users.BBL.Queries.GetUserProfile.Order")
    @patch("apps.users.BBL.Queries.GetUserProfile.GlobalCache")
    def test_serializer_called_with_expected_data(self, mock_cache, mock_order, mock_serializer):
        mock_cache.get.return_value = None
        fake_orders = MagicMock()
        fake_orders.count.return_value = 3
        fake_orders.__getitem__.return_value = ["order1"]
        mock_order.objects.filter.return_value.order_by.return_value = fake_orders

        mock_serializer_instance = MagicMock()
        mock_serializer_instance.data = {"ok": True}
        mock_serializer.return_value = mock_serializer_instance

        GetUserProfileSummaryQuery.query(self.user)

        # Ensure serializer called with dictionary containing key names
        args, _ = mock_serializer.call_args
        data_passed = args[0]
        assert "first_name" in data_passed
        assert "recent_orders" in data_passed
        assert "transactions" in data_passed
        assert "referral_code" in data_passed
