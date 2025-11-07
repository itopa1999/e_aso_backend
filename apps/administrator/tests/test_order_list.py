import pytest
from django.test import RequestFactory
from apps.aso.models import Order
from apps.users.models import User
from apps.administrator.BLL.Queries.OrderList import OrderListQuery
from django.utils import timezone
from datetime import timedelta

@pytest.mark.django_db
class TestOrderListQuery:
    def setup_method(self):
        
        now = timezone.now()
        
        
        self.factory = RequestFactory()
        self.user1 = User.objects.create(first_name="Lucky", last_name="Salawu", email="lucky@test.com")
        self.user2 = User.objects.create(first_name="Jane", last_name="Doe", email="jane@test.com")

        self.order1 = Order.objects.create(
            user=self.user1,
            created_at=now,
            subtotal=1500,
            shipping_fee=50,
            total=1550,
            order_number="ORD12345"
        )
        self.order2 = Order.objects.create(
            user=self.user2,
            created_at=now - timedelta(days=40),
            subtotal=1000,
            shipping_fee=30,
            total=1030,
            order_number="ORD67890"
        )

    def test_search_by_order_number(self):
        request = self.factory.get("/orders?search=12345")
        request.query_params = request.GET
        queryset = Order.objects.all()

        result = OrderListQuery.query(request, queryset)
        assert result.data.count() == 1
        assert result.data.first().order_number == "ORD12345"

    def test_search_by_user_name(self):
        request = self.factory.get("/orders?search=Lucky")
        request.query_params = request.GET
        queryset = Order.objects.all()

        result = OrderListQuery.query(request, queryset)
        assert result.data.count() == 1
        assert result.data.first().user.first_name == "Lucky"

    def test_search_by_id(self):
        request = self.factory.get(f"/orders?search={self.order2.id}")
        request.query_params = request.GET
        queryset = Order.objects.all()

        result = OrderListQuery.query(request, queryset)
        assert result.data.count() == 1
        assert result.data.first().id == self.order2.id
