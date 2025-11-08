# apps/aso/tests/test_product_list_query.py
import pytest
from apps.aso.BBL.Queries.Product.ProductList import ProductListQuery
from apps.aso.models import LookUp, Product
from utils.enum import LookUpsCategories

@pytest.mark.django_db
class TestProductListQuery:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Create categories
        self.cat_electronics = LookUp.objects.create(
            name="Electronics", category=LookUpsCategories.PRODUCT_CATEGORY
        )
        self.cat_fashion = LookUp.objects.create(
            name="Fashion", category=LookUpsCategories.PRODUCT_CATEGORY
        )

        # Create products
        self.prod1 = Product.objects.create(
            title="iPhone 15", current_price=12000, rating=4.5
        )
        self.prod1.category.set([self.cat_electronics])

        self.prod2 = Product.objects.create(
            title="Samsung Galaxy", current_price=9000, rating=4.0
        )
        self.prod2.category.set([self.cat_electronics])

        self.prod3 = Product.objects.create(
            title="Nike Sneakers", current_price=20000, rating=4.7
        )
        self.prod3.category.set([self.cat_fashion])

    def test_no_filters_returns_all(self):
        result = ProductListQuery.query({}, Product.objects.all())
        assert result.status_code == 200
        assert set(result.data) == {self.prod1, self.prod2, self.prod3}

    def test_filter_by_min_price(self):
        result = ProductListQuery.query({"min_price": 20000}, Product.objects.all())
        assert set(result.data) == {self.prod3}

    def test_filter_by_max_price(self):
        result = ProductListQuery.query({"max_price": 20000}, Product.objects.all())
        assert set(result.data) == {self.prod1, self.prod2, self.prod3}

    def test_filter_by_rating(self):
        result = ProductListQuery.query({"rating": 4.5}, Product.objects.all())
        assert list(result.data) == [self.prod1]

    def test_filter_by_category(self):
        result = ProductListQuery.query({"category": "Electronics"}, Product.objects.all())
        assert set(result.data) == {self.prod1, self.prod2}

    def test_filter_by_search(self):
        result = ProductListQuery.query({"search": "Samsung Galaxy"}, Product.objects.all())
        assert list(result.data) == [self.prod2]

        result2 = ProductListQuery.query({"search": "iPhone 15"}, Product.objects.all())
        assert list(result2.data) == [self.prod1]

        result3 = ProductListQuery.query({"search": "Electronics"}, Product.objects.all())
        assert set(result3.data) == {self.prod1, self.prod2}
