# import pytest
# from rest_framework.test import APIRequestFactory
# from rest_framework.request import Request
# from apps.aso.BBL.Queries.Product.ProductList import ProductListQuery
# from apps.aso.models import LookUp, Product
# from utils.enum import LookUpsCategories


# @pytest.mark.django_db
# class TestProductListQuery:
#     """Unit tests for ProductListQuery filtering logic."""

#     @pytest.fixture
#     def setup_products(self):
#         """Create sample categories and products for filtering."""
#         cat_electronics = LookUp.objects.create(
#             name="Electronics", category=LookUpsCategories.PRODUCT_CATEGORY
#         )
#         cat_fashion = LookUp.objects.create(
#             name="Fashion", category=LookUpsCategories.PRODUCT_CATEGORY
#         )

#         p1 = Product.objects.create(title="iPhone 15", current_price=1200, rating=4.5)
#         p1.category.set([cat_electronics])

#         p2 = Product.objects.create(title="Samsung Galaxy", current_price=900, rating=4.0)
#         p2.category.set([cat_electronics])

#         p3 = Product.objects.create(title="Nike Sneakers", current_price=200, rating=4.7)
#         p3.category.set([cat_fashion])

#         return [p1, p2, p3]

#     def make_request(self, query: str = ""):
#         """Helper to create a DRF Request with query params."""
#         factory = APIRequestFactory()
#         django_request = factory.get(f"/?{query}" if query else "/")
#         return Request(django_request)

#     def test_filter_by_min_price(self, setup_products):
#         request = self.make_request("min_price=1000")
#         queryset = Product.objects.all()

#         result = ProductListQuery.query(request, queryset)
#         data = result.data

#         assert result.status_code == 200
#         assert all(p.current_price >= 1000 for p in data)
#         assert len(data) == 1  # only iPhone 15

#     def test_filter_by_max_price(self, setup_products):
#         request = self.make_request("max_price=500")
#         queryset = Product.objects.all()

#         result = ProductListQuery.query(request, queryset)
#         data = result.data

#         assert all(p.current_price <= 500 for p in data)
#         assert len(data) == 1  # only Nike Sneakers

#     def test_filter_by_rating(self, setup_products):
#         request = self.make_request("rating=4.5")
#         queryset = Product.objects.all()

#         result = ProductListQuery.query(request, queryset)
#         data = result.data

#         assert all(p.rating >= 4.5 for p in data)
#         assert len(data) == 2  # iPhone + Nike Sneakers

#     def test_filter_by_category(self, setup_products):
#         request = self.make_request("category=Fashion")
#         queryset = Product.objects.all()

#         result = ProductListQuery.query(request, queryset)
#         data = result.data

#         assert all("Fashion" in [c.name for c in p.category.all()] for p in data)
#         assert len(data) == 1

#     def test_filter_by_search(self, setup_products):
#         request = self.make_request("search=iphone")
#         queryset = Product.objects.all()

#         result = ProductListQuery.query(request, queryset)
#         data = result.data

#         assert any("iphone" in p.title.lower() for p in data)
#         assert len(data) == 1

#     def test_no_filters_returns_all(self, setup_products):
#         request = self.make_request()
#         queryset = Product.objects.all()

#         result = ProductListQuery.query(request, queryset)

#         assert len(result.data) == 3
#         assert result.message == "Product list retrieved successfully."
