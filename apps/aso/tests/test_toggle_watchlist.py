import pytest
from http import HTTPStatus
from apps.aso.BBL.Commands.Watchlist.ToggleWatchlist import ToggleWatchlistCommand
from apps.aso.models import WatchList, Product


@pytest.mark.django_db
class TestToggleWatchlistCommand:
    def setup_method(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            email="watchlist@test.com",
            password="pass123"
        )
        self.product = Product.objects.create(
            title="Test Product",
            current_price=1000,
            rating=4.0
        )

    def test_adds_product_to_watchlist(self):
        """✅ Should add product to user's watchlist"""
        response = ToggleWatchlistCommand.execute(self.user, self.product.id)

        assert response.status_code == HTTPStatus.OK
        assert response.data["watchlisted"] is True
        assert WatchList.objects.filter(user=self.user, product=self.product, is_deleted=False).exists()

    def test_removes_product_from_watchlist_if_already_exists(self):
        """✅ Should remove product if already in watchlist"""
        WatchList.objects.create(user=self.user, product=self.product, is_deleted=False)

        response = ToggleWatchlistCommand.execute(self.user, self.product.id)

        assert response.status_code == HTTPStatus.OK
        assert response.data["watchlisted"] is False
        assert not WatchList.objects.filter(user=self.user, product=self.product, is_deleted=False).exists()

    def test_toggle_twice_adds_then_removes(self):
        """🌀 Running twice should first add then remove"""
        # First toggle adds
        first = ToggleWatchlistCommand.execute(self.user, self.product.id)
        assert first.data["watchlisted"] is True

        # Second toggle removes
        second = ToggleWatchlistCommand.execute(self.user, self.product.id)
        assert second.data["watchlisted"] is False
