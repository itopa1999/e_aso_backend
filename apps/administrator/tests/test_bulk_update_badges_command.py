import pytest
from unittest.mock import MagicMock
from apps.administrator.BLL.Commands.BulkUpdateProductBadges import BulkUpdateProductBadgesCommand
from apps.aso.models import Product
from django.utils import timezone

@pytest.mark.django_db
class TestBulkUpdateProductBadgesCommand:
    def setup_method(self):
        
        now = timezone.now()
        """Setup sample products and mock serializer/view"""
        self.product1 = Product.objects.create(title="iPhone 15", badge="Old", is_deleted=False, created_at=now, original_price=500)
        self.product2 = Product.objects.create(title="Nike Sneakers", badge="Old", is_deleted=False, created_at=now, original_price=100)
        self.product3 = Product.objects.create(title="Samsung Galaxy", badge="Old", is_deleted=False, created_at=now, original_price=700)

        # Mock view and serializer behavior
        self.mock_view = MagicMock()
        self.mock_serializer = MagicMock()
        self.mock_view.get_serializer.return_value = self.mock_serializer

    def test_update_by_ids(self):
        """Should update products using IDs"""
        request = MagicMock()
        request.data = {
            "badge": "New",
            "product_ids": [self.product1.id, self.product2.id]
        }

        self.mock_serializer.validated_data = request.data

        result = BulkUpdateProductBadgesCommand.execute(self.mock_view, request)

        assert result.status_code == 200
        assert result.data["updated_count"] == 2
        assert Product.objects.filter(badge="New").count() == 2

    def test_update_by_titles(self):
        """Should update products using titles"""
        request = MagicMock()
        request.data = {
            "badge": "Trending",
            "product_titles": ["Samsung Galaxy"]
        }

        self.mock_serializer.validated_data = request.data

        result = BulkUpdateProductBadgesCommand.execute(self.mock_view, request)

        assert result.status_code == 200
        assert result.data["updated_count"] == 1
        assert Product.objects.get(title="Samsung Galaxy").badge == "Trending"

    def test_update_with_empty_data(self):
        """Should not update any products when no IDs or titles are provided"""
        request = MagicMock()
        request.data = {"badge": "Hot"}  # No IDs or titles

        self.mock_serializer.validated_data = request.data

        result = BulkUpdateProductBadgesCommand.execute(self.mock_view, request)

        assert result.status_code == 200
        assert result.data["updated_count"] == 0
        assert Product.objects.filter(badge="Hot").count() == 0

    def test_update_with_mixed_ids_and_titles(self):
        """Should update using both IDs and titles"""
        request = MagicMock()
        request.data = {
            "badge": "Exclusive",
            "product_ids": [self.product1.id],
            "product_titles": ["Samsung Galaxy"]
        }

        self.mock_serializer.validated_data = request.data

        result = BulkUpdateProductBadgesCommand.execute(self.mock_view, request)

        assert result.status_code == 200
        assert result.data["updated_count"] == 2
        updated_titles = list(Product.objects.filter(badge="Exclusive").values_list("title", flat=True))
        assert sorted(updated_titles) == sorted(["iPhone 15", "Samsung Galaxy"])
