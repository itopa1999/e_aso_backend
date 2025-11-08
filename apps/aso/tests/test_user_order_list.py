import pytest
from unittest.mock import patch, MagicMock
from http import HTTPStatus
from apps.aso.BBL.Queries.Order.UserOrderList import UserOrderListQuery
from apps.aso.models import Order
from utils.base_result import BaseResultWithData


@pytest.mark.django_db
class TestUserOrderListQuery:

    def setup_method(self):
        self.user = MagicMock()
        self.user.id = 10
        self.request = MagicMock()
        self.request.user = self.user

    @patch("apps.aso.BBL.Queries.Order.UserOrderList.GlobalCache.get")
    def test_returns_cached_data(self, mock_cache_get):
        """Should return cached data if available."""
        mock_cache_get.return_value = {"data": [{"order_number": "ORD001"}]}

        result = UserOrderListQuery.query(self.request)

        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.OK
        assert result.data == [{"order_number": "ORD001"}]
        assert "fetched successfully" in result.message.lower()
        mock_cache_get.assert_called_once()

    @patch("apps.aso.BBL.Queries.Order.UserOrderList.GlobalCache")
    @patch("apps.aso.BBL.Queries.Order.UserOrderList.OrderSerializer")
    @patch("apps.aso.BBL.Queries.Order.UserOrderList.Order.objects.filter")
    def test_fetches_from_db_when_not_cached(
        self, mock_order_filter, mock_serializer, mock_cache
    ):
        """Should query DB and cache data when not found in cache."""
        mock_cache.get.return_value = None

        # Mock queryset and serializer
        fake_orders = [MagicMock(order_number="ORD002")]
        mock_order_filter.return_value.prefetch_related.return_value.order_by.return_value = fake_orders

        mock_serializer_instance = MagicMock()
        mock_serializer_instance.data = [{"order_number": "ORD002"}]
        mock_serializer.return_value = mock_serializer_instance

        result = UserOrderListQuery.query(self.request)

        # Assertions
        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.OK
        assert result.data == [{"order_number": "ORD002"}]
        assert "user orders fetched successfully" in result.message.lower()

        # Ensure DB and cache were called
        mock_order_filter.assert_called_once_with(user=self.user, is_deleted=False)
        mock_cache.set.assert_called_once()
        mock_serializer.assert_called_once_with(fake_orders, many=True, context={"request": self.request})
