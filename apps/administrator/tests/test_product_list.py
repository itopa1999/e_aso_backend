import pytest
from django.test import RequestFactory
from apps.administrator.BLL.Queries.ProductList import ProductListQuery
from apps.aso.models import LookUp, Product
from utils.enum import LookUpsCategories


@pytest.mark.django_db
class TestProductListQuery:
    def setup_method(self):
        """Setup test data"""
        self.factory = RequestFactory()

        # Create lookup categories
        self.cat_electronics = LookUp.objects.create(
            name="Electronics", category=LookUpsCategories.PRODUCT_CATEGORY
        )
        self.cat_fashion = LookUp.objects.create(
            name="Fashion", category=LookUpsCategories.PRODUCT_CATEGORY
        )

        # Create products
        self.p1 = Product.objects.create(
            title="iPhone 15", current_price=1200, rating=4.5
        )
        self.p1.category.set([self.cat_electronics])

        self.p2 = Product.objects.create(
            title="Samsung Galaxy", current_price=900, rating=4.0
        )
        self.p2.category.set([self.cat_electronics])

        self.p3 = Product.objects.create(
            title="Nike Sneakers", current_price=200, rating=4.7
        )
        self.p3.category.set([self.cat_fashion])

    def test_filter_by_min_price(self):
        """Products >= min_price should be returned"""
        request = self.factory.get("/products?min_price=1000")
        queryset = Product.objects.all()
        result = ProductListQuery.query(request, queryset)
        assert result.data.count() == 1
        assert result.data.first().title == "iPhone 15"

    def test_filter_by_max_price(self):
        """Products <= max_price should be returned"""
        request = self.factory.get("/products?max_price=500")
        queryset = Product.objects.all()
        result = ProductListQuery.query(request, queryset)
        assert result.data.count() == 1
        assert result.data.first().title == "Nike Sneakers"

    def test_filter_by_rating(self):
        request = self.factory.get("/products?rating=4.5")
        queryset = Product.objects.all()
        result = ProductListQuery.query(request, queryset)
        assert all(p.rating >= 4.5 for p in result.data)

    def test_filter_by_category(self):
        """Filter products by category name (ManyToMany)"""
        request = self.factory.get("/products?category=Fashion")
        queryset = Product.objects.all()
        result = ProductListQuery.query(request, queryset)
        assert result.data.count() == 1
        product = result.data.first()
        # Since category is ManyToMany, use .first()
        assert product.category.first().name == "Fashion"

    def test_filter_by_search(self):
        """Search should match title or category name"""
        request = self.factory.get("/products?search=iphone")
        queryset = Product.objects.all()
        result = ProductListQuery.query(request, queryset)
        assert result.data.count() == 1
        assert "iPhone" in result.data.first().title

    def test_combined_filters(self):
        """Should apply multiple filters together"""
        request = self.factory.get("/products?category=Electronics&min_price=800&max_price=1000")
        queryset = Product.objects.all()
        result = ProductListQuery.query(request, queryset)
        assert result.data.count() == 1
        assert result.data.first().title == "Samsung Galaxy"
