import pytest
from django.test import RequestFactory
from django.contrib.auth.models import Group
from apps.administrator.BLL.Queries.UserOrderList import UserListQuery
from apps.users.models import User
from utils.enum import GroupNames


@pytest.mark.django_db
class TestUserListQuery:
    def setup_method(self):
        self.factory = RequestFactory()

        # Create groups
        self.admin_group = Group.objects.create(name=GroupNames.ADMIN.value)
        self.customer_group = Group.objects.create(name=GroupNames.CUSTOMER.value)

        # Create users
        self.user1 = User.objects.create(
            first_name="Lucky",
            last_name="Salawu",
            email="lucky@example.com",
            phone="08123456789",
        )
        self.user1.groups.add(self.admin_group)

        self.user2 = User.objects.create(
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone="08098765432",
        )
        self.user2.groups.add(self.customer_group)

    def test_search_by_first_name(self):
        request = self.factory.get("/users?search=Lucky")
        request.query_params = request.GET
        queryset = User.objects.all()

        result = UserListQuery.query(request, queryset)
        assert result.data.count() == 1
        assert result.data.first().first_name == "Lucky"

    def test_search_by_email(self):
        request = self.factory.get("/users?search=jane@example.com")
        request.query_params = request.GET
        queryset = User.objects.all()

        result = UserListQuery.query(request, queryset)
        assert result.data.count() == 1
        assert result.data.first().email == "jane@example.com"

    def test_search_by_group(self):
        request = self.factory.get("/users?search=Admin")
        request.query_params = request.GET
        queryset = User.objects.all()

        result = UserListQuery.query(request, queryset)
        assert result.data.count() == 1
        assert result.data.first().groups.filter(name="Admin").exists()

    def test_search_by_phone(self):
        request = self.factory.get("/users?search=0809")
        request.query_params = request.GET
        queryset = User.objects.all()

        result = UserListQuery.query(request, queryset)
        assert result.data.count() == 1
        assert "0809" in result.data.first().phone
