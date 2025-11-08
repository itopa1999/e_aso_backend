import pytest
from http import HTTPStatus
from unittest.mock import patch

from apps.aso.BBL.Queries.Watchlist.GetWatchlistProducts import GetWatchlistProductsQuery
from apps.aso.models import Product, WatchList 
from utils.base_result import BaseResultWithData


@pytest.mark.django_db
class TestGetWatchlistProductsQuery:
    def setup_method(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        self.user = User.objects.create_user(
            email="watchlistuser@test.com",
            password="pass123"
        )
        self.product = Product.objects.create(
            title="Aso Oke Fabric",
            current_price=1200,
            rating=4.5,
            is_deleted=False
        )
        self.watchlist = WatchList.objects.create(
            user=self.user,
            product=self.product
        )

    @patch("apps.aso.BBL.Queries.Watchlist.GetWatchlistProducts.GlobalCache")
    def test_returns_data_from_cache_if_exists(self, mock_cache):
        """✅ Should return cached data if available"""
        mock_cache.get.return_value = {"data": [{"title": "Cached Product"}]}

        result = GetWatchlistProductsQuery.query(self.user)

        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.OK
        assert result.data[0]["title"] == "Cached Product"
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called()

    @patch("apps.aso.BBL.Queries.Watchlist.GetWatchlistProducts.GlobalCache")
    def test_fetches_from_db_when_cache_empty(self, mock_cache):
        """✅ Should query DB when cache is empty and then cache the result"""
        mock_cache.get.return_value = None

        result = GetWatchlistProductsQuery.query(self.user)

        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.OK
        assert len(result.data) == 1
        assert result.data[0]["title"] == "Aso Oke Fabric"
        mock_cache.set.assert_called_once()

    @patch("apps.aso.BBL.Queries.Watchlist.GetWatchlistProducts.GlobalCache")
    def test_returns_empty_list_if_no_watchlist(self, mock_cache):
        """⚙️ Should return empty list if user has no watchlist items"""
        mock_cache.get.return_value = None
        # Remove watchlist entries
        self.watchlist.delete()

        result = GetWatchlistProductsQuery.query(self.user)

        assert result.status_code == HTTPStatus.OK
        assert isinstance(result.data, list)
        assert len(result.data) == 0
        mock_cache.set.assert_called_once()

    @patch("apps.aso.BBL.Queries.Watchlist.GetWatchlistProducts.GlobalCache")
    def test_cache_key_is_generated_correctly(self, mock_cache):
        """🧩 Ensures correct cache key formatting"""
        mock_cache.get.return_value = None

        GetWatchlistProductsQuery.query(self.user)

        # Check that cache was queried using a properly formatted key like 'user_watchlist_4'
        args, kwargs = mock_cache.get.call_args
        cache_key = args[0]

        assert str(self.user.id) in cache_key
        assert "watchlist" in cache_key.lower()
