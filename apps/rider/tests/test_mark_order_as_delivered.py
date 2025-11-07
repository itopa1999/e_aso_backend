
import pytest
from http import HTTPStatus
from django.utils import timezone
from unittest.mock import patch
from apps.aso.models import Order, OrderTracking, OrderFeedBack
from apps.rider.BLL.Commands.MarkOrderAsDelivered import MarkOrderAsDeliveredCommand
from apps.users.models import User
from utils.base_result import BaseResultWithData


@pytest.mark.django_db
class TestMarkOrderAsDeliveredCommand:

    @pytest.fixture
    def user(self):
        return User.objects.create(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            password="securepassword"
        )

    @pytest.fixture
    def order(self, user):
        now = timezone.now()
        return Order.objects.create(
            user=user,
            order_number="ORD123",
            total=1000,
            created_at=now,
            subtotal=900,
            shipping_fee=100,
            is_deleted=False
        )

    def test_order_not_found(self):
        result = MarkOrderAsDeliveredCommand.execute(
            order_number="NONEXISTENT",
            rider="Rider1",
            delivery_notes="Delivered",
            stars=5
        )
        assert isinstance(result, BaseResultWithData)
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert result.message == "Order not found"

    @pytest.mark.parametrize("stars", [0, 6, "abc", None])
    def test_invalid_star_rating(self, order, stars):
        result = MarkOrderAsDeliveredCommand.execute(
            order_number=order.order_number,
            rider="Rider1",
            delivery_notes="Delivered",
            stars=stars
        )
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "star rating" in result.message

    @patch("apps.rider.BLL.Commands.MarkOrderAsDelivered.send_custom_email")
    def test_successful_delivery(self, mock_send_email, order):
        OrderTracking.objects.create(order=order, status="placed", date=timezone.now())
        OrderTracking.objects.create(order=order, status="processing", date=timezone.now())
        OrderTracking.objects.create(order=order, status="shipped", date=timezone.now())
        OrderTracking.objects.create(order=order, status="in_transit", date=timezone.now())
        result = MarkOrderAsDeliveredCommand.execute(
            order_number=order.order_number,
            rider=order.user,
            delivery_notes="Left at doorstep",
            stars=5
        )
        assert result.status_code == HTTPStatus.OK
        assert "delivered successfully" in result.message

        # Check tracking record
        tracking = OrderTracking.objects.filter(order=order, status="delivered").first()
        assert tracking is not None
        assert tracking.description == "Left at doorstep"
        assert tracking.completed is True

        # Check feedback record
        feedback = OrderFeedBack.objects.get(order=order)
        assert feedback.stars == 5
        assert feedback.comment == "Left at doorstep"

        # Check order fields updated
        order.refresh_from_db()
        assert order.dispatcher == order.user
        assert order.delivery_date is not None

        # Ensure email was sent
        mock_send_email.assert_called_once()
        args, kwargs = mock_send_email.call_args
        assert "Your order" in kwargs["message"]
        assert kwargs["recipient_email"] == order.user.email
