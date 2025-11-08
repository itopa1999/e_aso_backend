import pytest
from http import HTTPStatus
from apps.aso.BBL.Commands.Watchlist.RemoveAllWatchlist import RemoveAllWatchlistCommand
from apps.aso.models import WatchList, Product


@pytest.mark.django_db
class TestRemoveAllWatchlistCommand:
    def setup_method(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            email="clearwatch@test.com",
            password="pass123"
        )

        # Create sample products and watchlist items
        self.product1 = Product.objects.create(title="Fabric A", current_price=1000, rating=4.0)
        self.product2 = Product.objects.create(title="Fabric B", current_price=1200, rating=4.5)

        WatchList.objects.create(user=self.user, product=self.product1, is_deleted=False)
        WatchList.objects.create(user=self.user, product=self.product2, is_deleted=False)

    def test_removes_all_watchlist_items(self):
        """✅ Should remove all watchlist items for a user"""
        assert WatchList.objects.filter(user=self.user, is_deleted=False).count() == 2

        response = RemoveAllWatchlistCommand.execute(self.user)

        assert response.status_code == HTTPStatus.OK
        assert "deleted_count" in response.data
        assert response.data["deleted_count"] == 2
        assert WatchList.objects.filter(user=self.user, is_deleted=False).count() == 0

    def test_returns_zero_when_no_items_to_delete(self):
        """🧩 Should return 0 deleted when user has no watchlist items"""
        # First clear everything
        WatchList.objects.filter(user=self.user).delete()

        response = RemoveAllWatchlistCommand.execute(self.user)

        assert response.status_code == HTTPStatus.OK
        assert response.data["deleted_count"] == 0
        assert "removed" in response.message.lower()
