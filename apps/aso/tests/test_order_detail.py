import pytest
from http import HTTPStatus
from unittest.mock import patch, MagicMock
from apps.aso.BBL.Queries.Order.OrderDetails import OrderDetailQuery
from apps.aso.models import Order
from utils.base_result import BaseResultWithData


@pytest.mark.django_db
class TestOrderDetailQuery:

    def setup_method(self):
        # Create a fake user for testing
        from django.contrib.auth import get_user_model
        self.user = get_user_model().objects.create_user(
            email="testuser@gmail.com", password="testpass"
        )

    @patch("apps.aso.BBL.Queries.Order.OrderDetails.GlobalCache")
    def test_query_returns_cached_data(self, mock_cache):
        """✅ Should return cached data if it exists"""
        cached_response = {"data": {"id": 1, "status": "delivered"}}
        mock_cache.get.return_value = cached_response

        result = OrderDetailQuery.query(self.user, order_id=1)

        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.OK
        assert result.data == cached_response["data"]
        mock_cache.get.assert_called_once()

    @patch("apps.aso.BBL.Queries.Order.OrderDetails.GlobalCache")
    @patch("apps.aso.BBL.Queries.Order.OrderDetails.OrderDetailSerializer")
    def test_query_fetches_from_db_when_not_cached(self, mock_serializer, mock_cache):
        """✅ Should fetch order from DB, serialize and cache it when not cached"""
        mock_cache.get.return_value = None

        order = Order.objects.create(user=self.user, total=5000, subtotal=4500, shipping_fee=500, is_deleted=False)
        mock_serializer.return_value.data = {"id": order.id, "total": 5000, "subtotal": 4500, "shipping_fee": 500}

        result = OrderDetailQuery.query(self.user, order.id)

        assert result.status_code == HTTPStatus.OK
        assert result.data["id"] == order.id
        mock_cache.set.assert_called_once()
        mock_serializer.assert_called_once()

    @patch("apps.aso.BBL.Queries.Order.OrderDetails.GlobalCache")
    def test_query_returns_not_found_if_order_does_not_exist(self, mock_cache):
        """❌ Should return NOT_FOUND if order does not exist"""
        mock_cache.get.return_value = None

        result = OrderDetailQuery.query(self.user, order_id=999)

        assert result.status_code == HTTPStatus.NOT_FOUND
        assert result.data is None
        assert "not found" in result.message.lower()
