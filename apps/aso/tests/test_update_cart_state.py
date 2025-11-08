import pytest
from http import HTTPStatus
from django.contrib.auth import get_user_model
from apps.aso.BBL.Commands.Cart.UpdateCartState import UpdateCartStateCommand
from apps.aso.models import Cart


@pytest.mark.django_db
class TestUpdateCartStateCommand:
    def setup_method(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="cartstate@test.com",
            password="password123"
        )

    def test_update_existing_cart_state(self):
        """✅ Should update state of an existing cart"""
        cart = Cart.objects.create(user=self.user, state="pending", is_deleted=False)

        new_state = "completed"
        result = UpdateCartStateCommand.execute(self.user, new_state)

        assert result.status_code == HTTPStatus.OK
        assert result.data["cart_id"] == cart.id
        assert result.data["state"] == new_state
        assert "cart state updated" in result.message.lower()

        cart.refresh_from_db()
        assert cart.state == new_state

    def test_create_cart_and_set_state_if_none_exists(self):
        """✅ Should create cart if none exists and set the state"""
        new_state = "processing"
        result = UpdateCartStateCommand.execute(self.user, new_state)

        cart = Cart.objects.get(user=self.user, is_deleted=False)
        assert result.status_code == HTTPStatus.OK
        assert result.data["cart_id"] == cart.id
        assert result.data["state"] == new_state
        assert cart.state == new_state
