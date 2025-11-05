import pytest
from http import HTTPStatus
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import Group
from apps.administrator.BLL.Queries.Dashboard import DashboardQuery
from apps.aso.models import Product, Order, OrderItem, OrderTracking
from apps.users.models import User
from utils.enum import GroupNames


@pytest.mark.django_db
class TestDashboardQuery:

    @pytest.fixture
    def sample_data(self):
        """Create minimal data for dashboard metrics."""
        now = timezone.now()

        # Create users
        customer = User.objects.create(email="cust1@example.com")
        rider = User.objects.create(email="rider1@example.com")

        # Assign groups (assuming GroupNames has CUSTOMER and RIDER)
        customer_group, _ = Group.objects.get_or_create(name=GroupNames.CUSTOMER.value)
        rider_group, _ = Group.objects.get_or_create(name=GroupNames.RIDER.value)

        customer.groups.add(customer_group)
        rider.groups.add(rider_group)
        customer.save()
        rider.save()

        # Create products
        product1 = Product.objects.create(title="Phone", created_at=now, original_price=500)
        product2 = Product.objects.create(title="Laptop", created_at=now - timedelta(days=40), original_price=1000)

        # Create orders
        order1 = Order.objects.create(user=customer, created_at=now, subtotal=1500, shipping_fee=50, total=1550)
        order2 = Order.objects.create(user=customer, created_at=now - timedelta(days=40), subtotal=1000, shipping_fee=30, total=1030)

        # Create order items
        OrderItem.objects.create(order=order1, product=product1, quantity=2, price=500)
        OrderItem.objects.create(order=order2, product=product2, quantity=1, price=1000)

        # Create tracking placed
        OrderTracking.objects.create(order=order1, status="placed", date=now)
        OrderTracking.objects.create(order=order2, status="placed", date=now - timedelta(days=40))

        return {
            "customer": customer,
            "rider": rider,
            "product1": product1,
            "product2": product2,
            "order1": order1,
            "order2": order2,
        }

    def test_dashboard_query_success(self, client, sample_data):
        """Should return dashboard metrics successfully."""
        request = client.get("/")
        result = DashboardQuery.query(request.wsgi_request)

        assert result.status_code == HTTPStatus.OK
        data = result.data

        # Check major keys
        assert "stats" in data
        assert "order_status" in data
        assert "top_products" in data
        assert "recent_orders" in data

        # Validate "order_status" structure
        order_stats = data["order_status"]
        expected_keys = {"total_products", "total_orders", "total_customers", "total_users", "total_riders"}
        assert expected_keys.issubset(order_stats.keys())

        # Each metric should have "value", "change", and "direction"
        for metric in order_stats.values():
            assert "value" in metric
            assert "change" in metric
            assert "direction" in metric

        # Top products should not be empty since we created some
        assert isinstance(data["top_products"], list)
        assert len(data["top_products"]) >= 1

        # Stats (status counts)
        assert isinstance(data["stats"], list)
        assert all("name" in s and "value" in s for s in data["stats"])

        # Recent orders list
        assert isinstance(data["recent_orders"], list)

    def test_dashboard_query_empty(self, client):
        """Should return default values even when no data exists."""
        request = client.get("/")
        result = DashboardQuery.query(request.wsgi_request)

        assert result.status_code == HTTPStatus.OK
        data = result.data

        assert "order_status" in data
        for metric in data["order_status"].values():
            assert "value" in metric
            assert "change" in metric
            assert "direction" in metric
