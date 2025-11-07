import pytest
from decimal import Decimal
from apps.aso.models import LookUp, Product, ProductSize, ProductColor, ProductDetail
from apps.administrator.serializers import ProductImportSerializer
from utils.enum import LookUpsCategories


@pytest.mark.django_db
class TestProductImportSerializer:
    def setup_method(self):
        # Prepare lookup categories for badges & product categories
        self.badge_lookup = LookUpsCategories.BADGE_CATEGORY
        self.category_lookup = LookUpsCategories.PRODUCT_CATEGORY

    def test_create_product_with_new_lookups(self):
        """Should create a product and auto-create category & badge lookups"""
        data = {
            "title": "Nike Air Zoom",
            "badge": "Hot Deal",
            "description": "Comfortable running shoes",
            "original_price": "25000.00",
            "discount_percent": 10,
            "rating": 4.5,
            "category": ["Shoes", "Sportswear"],
            "sizes": ["M", "L"],
            "colors": [
                {"name": "Black", "hex": "#000000"},
                {"name": "White", "hex": "#FFFFFF"},
            ],
            "details": [
                {"tab": "description", "content": "This is the overview"},
                {"tab": "shipping", "content": "Made from recycled fabric"},
            ],
        }

        serializer = ProductImportSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        product = serializer.save()

        assert Product.objects.count() == 1
        assert product.title == "Nike Air Zoom"
        assert product.original_price == Decimal("25000.00")
        assert product.rating == 4.5
        assert product.display_product is False

        badge_lookup = LookUp.objects.filter(
            name__iexact="Hot Deal",
            category=self.badge_lookup,
        ).first()
        assert badge_lookup is not None
        assert product.badge == "Hot Deal"

        categories = LookUp.objects.filter(category=self.category_lookup)
        assert categories.count() == 2
        assert set(c.name for c in categories) == {"Shoes", "Sportswear"}

        assert product.category.count() == 2

        sizes = ProductSize.objects.filter(product=product)
        assert sizes.count() == 2
        assert {s.size_label for s in sizes} == {"M", "L"}

        colors = ProductColor.objects.filter(product=product)
        assert colors.count() == 2
        assert {c.color_name for c in colors} == {"Black", "White"}

        details = ProductDetail.objects.filter(product=product)
        assert details.count() == 2
        assert details.first().tab in {"description", "shipping"}

    def test_existing_lookup_reused(self):
        """Should reuse existing LookUp instead of creating a new one"""
        existing_cat = LookUp.objects.create(
            name="Shoes",
            category=self.category_lookup
        )
        existing_badge = LookUp.objects.create(
            name="Limited Offer",
            category=self.badge_lookup
        )

        data = {
            "title": "Adidas Runner",
            "badge": "Limited Offer",
            "description": "Lightweight running shoes",
            "original_price": "30000.00",
            "rating": 4.7,
            "category": ["Shoes"],
            "sizes": [],
            "colors": [],
            "details": [],
        }

        serializer = ProductImportSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        product = serializer.save()

        # Should not create duplicates
        assert LookUp.objects.filter(name="Shoes", category=self.category_lookup).count() == 1
        assert LookUp.objects.filter(name="Limited Offer", category=self.badge_lookup).count() == 1
        assert product.badge == "Limited Offer"
