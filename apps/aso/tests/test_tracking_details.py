import pytest
from http import HTTPStatus
from unittest.mock import patch, MagicMock

from apps.aso.BBL.Queries.Order.TrackingDetails import TrackingDetailsQuery
from apps.aso.models import Order
from utils.base_result import BaseResultWithData


@pytest.mark.django_db
class TestTrackingDetailsQuery:

    def setup_method(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            email="tracking@test.com",
            password="pass123"
        )
        self.order = Order.objects.create(user=self.user, total=2500, shipping_fee=200, subtotal=2300, is_deleted=False)

    @patch("apps.aso.BBL.Queries.Order.TrackingDetails.GlobalCache.get")
    def test_query_returns_cached_data(self, mock_cache_get):
        """✅ Returns cached tracking details when available"""
        mock_cache_get.return_value = {"data": {"order_id": 1, "status": "Cached"}}

        result = TrackingDetailsQuery.query(self.user, self.order.id)

        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.OK
        assert result.data["status"] == "Cached"
        mock_cache_get.assert_called_once()

    @patch("apps.aso.BBL.Queries.Order.TrackingDetails.GlobalCache")
    @patch("apps.aso.BBL.Queries.Order.TrackingDetails.OrderTrackingDetailsSerializer")
    def test_query_fetches_from_db_and_sets_cache(self, mock_serializer, mock_cache):
        """✅ Fetches from DB when cache is empty and sets cache"""
        mock_cache.get.return_value = None
        mock_serializer.return_value.data = {"order_id": self.order.id, "status": "In Transit"}

        result = TrackingDetailsQuery.query(self.user, self.order.id)

        assert result.status_code == HTTPStatus.OK
        assert "In Transit" in result.data["status"]
        mock_cache.set.assert_called_once()
        mock_serializer.assert_called_once()

    def test_query_returns_bad_request_when_order_not_found(self):
        """❌ Returns BAD_REQUEST when order does not exist"""
        result = TrackingDetailsQuery.query(self.user, 99999)

        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert result.data is None
        assert "not found" in result.message.lower()
