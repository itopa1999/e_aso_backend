import pytest
from unittest.mock import patch, MagicMock
from http import HTTPStatus
from apps.aso.BBL.Queries.Product.ProductDetails import ProductDetailQuery
from apps.aso.models import Product

@pytest.mark.django_db
class TestProductDetailQuery:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.product = Product.objects.create(
            title="Aso Oke Fabric",
            current_price=1200,
            rating=4.5,
            display_product=True,
            is_deleted=False,
            reviews_count=0
        )
        self.deleted_product = Product.objects.create(
            title="Deleted Product",
            current_price=1000,
            rating=4.0,
            display_product=True,
            is_deleted=True
        )

    @patch("apps.aso.BBL.Queries.Product.ProductDetails.GlobalCache")
    def test_returns_cached_product_if_exists(self, mock_cache):
        mock_cache.get.return_value = {"data": self.product}

        result = ProductDetailQuery.query(self.product.id)

        mock_cache.get.assert_called_once()
        assert result.status_code == HTTPStatus.OK
        assert result.data == self.product
        assert "fetched successfully" in result.message.lower()

    @patch("apps.aso.BBL.Queries.Product.ProductDetails.GlobalCache")
    def test_returns_product_and_sets_cache_if_not_cached(self, mock_cache):
        mock_cache.get.return_value = None

        result = ProductDetailQuery.query(self.product.id)

        mock_cache.set.assert_called_once()
        assert result.status_code == HTTPStatus.OK
        assert result.data.id == self.product.id
        assert result.data.reviews_count == 1
        assert "retrieved successfully" in result.message.lower()

    @patch("apps.aso.BBL.Queries.Product.ProductDetails.GlobalCache")
    def test_returns_not_found_for_missing_or_deleted_product(self, mock_cache):
        mock_cache.get.return_value = None

        result = ProductDetailQuery.query(self.deleted_product.id)
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert result.data is None
        assert "not found" in result.message.lower()

        result2 = ProductDetailQuery.query(9999)  # non-existent ID
        assert result2.status_code == HTTPStatus.NOT_FOUND
        assert result2.data is None
