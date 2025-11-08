import pytest
from unittest.mock import patch, MagicMock
from http import HTTPStatus
from django.contrib.auth import get_user_model
from apps.aso.BBL.Queries.Cart.GetCartDetails import GetCartDetailQuery
from apps.aso.models import Cart


@pytest.mark.django_db
class TestGetCartDetailQuery:
    def setup_method(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="cartquery@test.com",
            password="pass123"
        )

        # Simulate request with user
        class DummyRequest:
            def __init__(self, user):
                self.user = user
                self.query_params = {}

        self.request = DummyRequest(self.user)

    @patch("apps.aso.BBL.Queries.Cart.GetCartDetails.GlobalCache")
    @patch("apps.aso.BBL.Queries.Cart.GetCartDetails.CartDetailSerializer")
    def test_returns_cached_data_if_available(self, mock_serializer, mock_cache):
        """✅ Should return cached data when cache exists"""
        mock_cache.get.return_value = {"data": {"id": 1, "items": []}}

        result = GetCartDetailQuery.query(self.request)

        assert result.status_code == HTTPStatus.OK
        assert result.data == {"id": 1, "items": []}
        assert "fetched successfully" in result.message.lower()
        mock_cache.get.assert_called_once()

    @patch("apps.aso.BBL.Queries.Cart.GetCartDetails.GlobalCache")
    @patch("apps.aso.BBL.Queries.Cart.GetCartDetails.CartDetailSerializer")
    def test_creates_cart_and_sets_cache_when_not_cached(self, mock_serializer, mock_cache):
        """🧩 Should fetch from DB and store in cache when no cached data"""
        mock_cache.get.return_value = None
        mock_serializer.return_value.data = {"id": 1, "items": []}

        result = GetCartDetailQuery.query(self.request)

        assert result.status_code == HTTPStatus.OK
        assert result.data == {"id": 1, "items": []}
        assert "retrieved successfully" in result.message.lower()

        # Ensure cache was written
        mock_cache.set.assert_called_once()

        # Ensure cart was created
        assert Cart.objects.filter(user=self.user).exists()

    @patch("apps.aso.BBL.Queries.Cart.GetCartDetails.GlobalCache")
    @patch("apps.aso.BBL.Queries.Cart.GetCartDetails.CartDetailSerializer")
    def test_existing_cart_is_used(self, mock_serializer, mock_cache):
        """🧺 Should use existing cart if already created"""
        Cart.objects.create(user=self.user, is_deleted=False)
        mock_cache.get.return_value = None
        mock_serializer.return_value.data = {"id": 1, "items": []}

        result = GetCartDetailQuery.query(self.request)

        assert result.status_code == HTTPStatus.OK
        mock_cache.set.assert_called_once()
        mock_serializer.assert_called_once()
        assert Cart.objects.filter(user=self.user).count() == 1
