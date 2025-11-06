import pytest
from http import HTTPStatus
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from apps.administrator.BLL.Queries.Dashboard import DashboardQuery
from apps.aso.models import Product, Order, OrderItem, OrderTracking
from apps.users.models import User
from utils.enum import GroupNames


@pytest.mark.django_db
class TestDashboardQuery:
    """Tests for DashboardQuery (admin dashboard metrics)."""

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def sample_data(self):
        """Create minimal test data for dashboard metrics."""
        now = timezone.now()

        # Create users
        customer = User.objects.create(email="cust1@example.com")
        rider = User.objects.create(email="rider1@example.com")

        # Assign groups
        customer_group, _ = Group.objects.get_or_create(name=GroupNames.CUSTOMER.value)
        rider_group, _ = Group.objects.get_or_create(name=GroupNames.RIDER.value)

        customer.groups.add(customer_group)
        rider.groups.add(rider_group)

        # Create products
        product1 = Product.objects.create(
            title="Phone", created_at=now, original_price=500
        )
        product2 = Product.objects.create(
            title="Laptop", created_at=now - timedelta(days=40), original_price=1000
        )

        # Create orders
        order1 = Order.objects.create(
            user=customer,
            created_at=now,
            subtotal=1500,
            shipping_fee=50,
            total=1550,
        )
        order2 = Order.objects.create(
            user=customer,
            created_at=now - timedelta(days=40),
            subtotal=1000,
            shipping_fee=30,
            total=1030,
        )

        # Create order items
        OrderItem.objects.create(order=order1, product=product1, quantity=2, price=500)
        OrderItem.objects.create(order=order2, product=product2, quantity=1, price=1000)

        # Create order tracking
        OrderTracking.objects.create(order=order1, status="placed", date=now)
        OrderTracking.objects.create(
            order=order2, status="placed", date=now - timedelta(days=40)
        )

        return {
            "customer": customer,
            "rider": rider,
            "product1": product1,
            "product2": product2,
            "order1": order1,
            "order2": order2,
        }

    def test_dashboard_query_success(self, client, sample_data):
        """Should return valid dashboard metrics with data."""
        request = client.get("/")
        result = DashboardQuery.query(request.wsgi_request)

        assert result.status_code == HTTPStatus.OK

        data = result.data
        assert isinstance(data, dict)

        # Validate top-level keys
        expected_keys = {"stats", "order_status", "top_products", "recent_orders"}
        assert expected_keys.issubset(data.keys())

        # Validate order_status structure
        order_status = data["order_status"]
        required_fields = {"total_products", "total_orders", "total_customers", "total_users", "total_riders"}
        assert required_fields.issubset(order_status.keys())

        for metric in order_status.values():
            assert all(k in metric for k in ("value", "change", "direction"))

        # Top products section
        assert isinstance(data["top_products"], list)
        assert len(data["top_products"]) >= 1

        # Stats section
        assert isinstance(data["stats"], list)
        assert all("name" in s and "value" in s for s in data["stats"])

        # Recent orders section
        assert isinstance(data["recent_orders"], list)

    def test_dashboard_query_empty(self, client):
        """Should return default metrics when no data exists."""
        request = client.get("/")
        result = DashboardQuery.query(request.wsgi_request)

        assert result.status_code == HTTPStatus.OK
        data = result.data

        assert "order_status" in data
        for metric in data["order_status"].values():
            assert all(k in metric for k in ("value", "change", "direction"))
