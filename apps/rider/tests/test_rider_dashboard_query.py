import pytest
from django.utils import timezone
from apps.aso.models import Order, User
from apps.rider.BLL.Queries.RiderDashboard import RiderDashboardQuery
from utils.base_result import BaseResultWithData
from django.utils import timezone
@pytest.mark.django_db
class TestRiderDashboardQuery:
    @pytest.fixture
    
    def rider(self):
        return User.objects.create(
            first_name="John",
            last_name="Doe",
            email="rider@example.com",
            rider_number="R123"
        )

    @pytest.fixture
    def orders(self, rider):
        
        now = timezone.now()
        # Delivered orders
        order1 = Order.objects.create(
            user=User.objects.create(first_name="Alice", last_name="Smith", email="alice@example.com"),
            dispatcher=rider,
            order_number="ORD001",
            total=100,
            created_at=now,
            subtotal=1500,
            shipping_fee=50,
            delivery_date=timezone.now()
        )
        order2 = Order.objects.create(
            user=User.objects.create(first_name="Bob", last_name="Brown", email="bob@example.com"),
            dispatcher=rider,
            order_number="ORD002",
            total=50,
            created_at=now,
            subtotal=500,
            shipping_fee=50,
            delivery_date=timezone.now()
        )
        # Undelivered order
        Order.objects.create(
            user=User.objects.create(first_name="Charlie", last_name="Davis", email="charlie@example.com"),
            dispatcher=rider,
            order_number="ORD003",
            total=30,
            created_at=now,
            subtotal=300,
            shipping_fee=30,
            delivery_date=None
        )
        return [order1, order2]

    def test_rider_dashboard_no_search(self, rider, orders):
        result = RiderDashboardQuery.query(rider)
        assert isinstance(result, BaseResultWithData)
        assert result.status_code == 200
        profile = result.data["profile"]
        recent_orders = result.data["recent_deliveries"]
        assert profile["name"] == "John Doe"
        assert profile["rider_id"] == "R123"
        assert profile["deliveries_count"] == 2  # only delivered orders counted
        assert recent_orders.count() == 2

    def test_rider_dashboard_with_search(self, rider, orders):
        # Search by user first name
        result = RiderDashboardQuery.query(rider, search="Alice")
        recent_orders = result.data["recent_deliveries"]
        assert recent_orders.count() == 1
        assert recent_orders.first().user.first_name == "Alice"

        # Search by order_number
        result2 = RiderDashboardQuery.query(rider, search="ORD002")
        recent_orders2 = result2.data["recent_deliveries"]
        assert recent_orders2.count() == 1
        assert recent_orders2.first().order_number == "ORD002"
