# apps/aso/tests/test_cart_watchlist_count.py
import pytest
from django.contrib.auth import get_user_model
from apps.aso.BBL.Queries.CartAndWatchlistCount import CartAndWatchlistCountQuery
from apps.aso.models import Cart, CartItem, WatchList, Product
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys

User = get_user_model()

@pytest.mark.django_db
class TestCartAndWatchlistCountQuery:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = User.objects.create_user(email="testuser@example.com", password="pass123")
        
        # Create Cart and CartItem
        self.cart = Cart.objects.create(user=self.user, is_deleted=False)
        self.product1 = Product.objects.create(title="Product 1", current_price=100)
        self.product2 = Product.objects.create(title="Product 2", current_price=200)
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1)
        
        # Create WatchList items
        self.watchlist_product = Product.objects.create(title="Watch Product", current_price=150)
        WatchList.objects.create(user=self.user, product=self.watchlist_product, is_deleted=False)
        
        # Clear cache before each test
        GlobalCache.clear()

    def test_query_returns_correct_counts(self):
        result = CartAndWatchlistCountQuery.query(self.user)
        assert result.status_code == 200
        assert result.data["item_count"] == 2  # 2 items in cart
        assert result.data["watchlist_count"] == 1

    def test_query_uses_cache_if_available(self):
        cache_key = CacheKeys.format(CacheKeys.USER_WATCHLISTCART, user_id=self.user.id)
        GlobalCache.set(cache_key, {"data": {"item_count": 99, "watchlist_count": 42}})

        result = CartAndWatchlistCountQuery.query(self.user)
        assert result.data["item_count"] == 99
        assert result.data["watchlist_count"] == 42

    def test_query_handles_no_cart(self):
        # Delete cart to simulate user without cart
        self.cart.delete()
        result = CartAndWatchlistCountQuery.query(self.user)
        assert result.data["item_count"] == 0
        assert result.data["watchlist_count"] == 1

    def test_query_handles_no_watchlist(self):
        # Delete all watchlist items
        WatchList.objects.filter(user=self.user).delete()
        result = CartAndWatchlistCountQuery.query(self.user)
        assert result.data["item_count"] == 2
        assert result.data["watchlist_count"] == 0
