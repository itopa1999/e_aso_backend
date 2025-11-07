# File: apps/rider/tests/test_rider_order_details_query.py

import pytest
from http import HTTPStatus
from django.utils import timezone
from apps.aso.models import Order, Product, ShippingAddress, OrderItem
from apps.rider.BLL.Queries.RiderOrderDetails import RiderOrderDetailsQuery
from apps.users.models import User
from utils.base_result import BaseResultWithData


@pytest.mark.django_db
class TestRiderOrderDetailsQuery:

    @pytest.fixture
    def user(self):
        return User.objects.create(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            password="securepassword"
        )

    @pytest.fixture
    def product(self):
        now = timezone.now()
        return Product.objects.create(
            title="Test Product",
            created_at=now, original_price=500
        )

    @pytest.fixture
    def order(self, user):
        now = timezone.now()
        order = Order.objects.create(
            user=user,
            order_number="ORD123",
            total=5000,
            created_at=now,
            subtotal=4500,
            shipping_fee=500,
            is_deleted=False
        )
        ShippingAddress.objects.create(
            order=order,
            first_name=user.first_name,
            last_name=user.last_name,
            address="123 Main St",
            apartment="",
            city="Lagos",
            state="Lagos",
            phone="08012345678",
            alt_phone=""
        )
        return order

    @pytest.fixture
    def order_item(self, order, product):
        return OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            price=product.original_price,
            desc="Test item"
        )

    def mock_request(self):
        # Dummy request object for build_absolute_uri
        class DummyRequest:
            def build_absolute_uri(self, x):
                return f"http://testserver{x}"
        return DummyRequest()

    def test_order_not_found(self):
        request = self.mock_request()
        result = RiderOrderDetailsQuery.execute("NONEXISTENT", request)
        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert result.message == "Order not found"

    def test_order_details_success(self, order, order_item):
        request = self.mock_request()
        result = RiderOrderDetailsQuery.execute(order.order_number, request)
        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.OK
        assert result.message == "Success"

        data = result.data
        assert data["order_id"] == order.order_number
        assert data["customer"] == f"{order.user.first_name} {order.user.last_name}"
        assert "123 Main St" in data["delivery_address"]
        assert data["contact"] == "08012345678"
        assert len(data["items"]) == 1
        assert data["items"][0]["product"] == "Test Product"
        assert data["items"][0]["quantity"] == 2
