# import pytest
# from rest_framework.test import APIRequestFactory
# from apps.aso.BBL.Queries.Product.ProductList import ProductListQuery
# from apps.aso.models import LookUp, Product
# from utils.enum import LookUpsCategories


# @pytest.mark.django_db
# class TestProductListQuery:

#     @pytest.fixture
#     def setup_products(self):
#         """Create sample categories and products for filtering."""
#         cat_electronics = LookUp.objects.create(
#             name="Electronics", category=LookUpsCategories.PRODUCT_CATEGORY
#         )
#         cat_fashion = LookUp.objects.create(
#             name="Fashion", category=LookUpsCategories.PRODUCT_CATEGORY
#         )

#         p1 = Product.objects.create(
#             title="iPhone 15",
#             current_price=1200,
#             rating=4.5,
#         )
#         p1.category.set([cat_electronics])

#         p2 = Product.objects.create(
#             title="Samsung Galaxy",
#             current_price=900,
#             rating=4.0,
#         )
#         p2.category.set([cat_electronics])

#         p3 = Product.objects.create(
#             title="Nike Sneakers",
#             current_price=200,
#             rating=4.7,
#         )
#         p3.category.set([cat_fashion])

#         return [p1, p2, p3]

#     def test_filter_by_min_price(self, setup_products):
#         factory = APIRequestFactory()
#         request = factory.get("/?min_price=1000")

#         queryset = Product.objects.all()
#         result = ProductListQuery.query(request, queryset)

#         assert result.status_code == 200
#         data = result.data
#         assert all(p.current_price >= 1000 for p in data)
#         assert len(data) == 1  # only iPhone 15

#     def test_filter_by_max_price(self, setup_products):
#         factory = APIRequestFactory()
#         request = factory.get("/?max_price=500")

#         queryset = Product.objects.all()
#         result = ProductListQuery.query(request, queryset)

#         data = result.data
#         assert all(p.current_price <= 500 for p in data)
#         assert len(data) == 1  # only Nike Sneakers

#     def test_filter_by_rating(self, setup_products):
#         factory = APIRequestFactory()
#         request = factory.get("/?rating=4.5")

#         queryset = Product.objects.all()
#         result = ProductListQuery.query(request, queryset)

#         data = result.data
#         assert all(p.rating >= 4.5 for p in data)
#         assert len(data) == 2  # iPhone + Nike Sneakers

#     def test_filter_by_category(self, setup_products):
#         factory = APIRequestFactory()
#         request = factory.get("/?category=Fashion")

#         queryset = Product.objects.all()
#         result = ProductListQuery.query(request, queryset)

#         data = result.data
#         assert all("Fashion" in [c.name for c in p.category.all()] for p in data)
#         assert len(data) == 1

#     def test_filter_by_search(self, setup_products):
#         factory = APIRequestFactory()
#         request = factory.get("/?search=iphone")

#         queryset = Product.objects.all()
#         result = ProductListQuery.query(request, queryset)

#         data = result.data
#         assert any("iphone" in p.title.lower() for p in data)
#         assert len(data) == 1

#     def test_no_filters_returns_all(self, setup_products):
#         factory = APIRequestFactory()
#         request = factory.get("/")

#         queryset = Product.objects.all()
#         result = ProductListQuery.query(request, queryset)

#         assert len(result.data) == 3
#         assert result.message == "Product list retrieved successfully."
