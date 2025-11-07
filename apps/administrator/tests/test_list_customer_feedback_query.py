import pytest
from datetime import datetime, date
from types import SimpleNamespace
from django.utils import timezone
from apps.administrator.BLL.Queries.ListCustomerFeedback import ListCustomerFeedbackQuery
from apps.administrator.models import CustomerFeedback
from utils.base_result import BaseResultWithData


@pytest.mark.django_db
class TestListCustomerFeedbackQuery:
    @pytest.fixture
    def feedbacks(self):
        # Fixed base dates (instead of timezone.now())
        base_dates = [
            timezone.make_aware(datetime(2025, 1, 1)),  # Alice
            timezone.make_aware(datetime(2025, 1, 5)),  # Bob
            timezone.make_aware(datetime(2025, 1, 10)), # Charlie
        ]

        alice = CustomerFeedback.objects.create(
            user="Alice", feedback="Great support!", rating=5
        )
        CustomerFeedback.objects.filter(pk=alice.pk).update(created_at=base_dates[0])

        bob = CustomerFeedback.objects.create(
            user="Bob", feedback="Good but can improve", rating=4
        )
        CustomerFeedback.objects.filter(pk=bob.pk).update(created_at=base_dates[1])

        charlie = CustomerFeedback.objects.create(
            user="Charlie", feedback="Average experience", rating=3
        )
        CustomerFeedback.objects.filter(pk=charlie.pk).update(created_at=base_dates[2])
        return [alice, bob, charlie]

    def mock_request(self, params):
        return SimpleNamespace(query_params=params)

    def test_returns_all_feedbacks_without_filters(self, feedbacks):
        request = self.mock_request({})
        queryset = CustomerFeedback.objects.all()

        result = ListCustomerFeedbackQuery.query(queryset, request)

        assert isinstance(result, BaseResultWithData)
        assert result.status_code == 200
        assert result.data.count() == len(feedbacks)

    def test_filters_by_name(self, feedbacks):
        request = self.mock_request({"name": "Alice"})
        queryset = CustomerFeedback.objects.all()
        result = ListCustomerFeedbackQuery.query(queryset, request)
        assert result.data.count() == 1
        assert result.data.first().user == "Alice"

    def test_filters_by_start_date(self, feedbacks):
        # Should include records created after Jan 3
        request = self.mock_request({"start_date": date(2025, 1, 3).isoformat()})
        queryset = CustomerFeedback.objects.all()

        result = ListCustomerFeedbackQuery.query(queryset, request)
        users = set(result.data.values_list("user", flat=True))

        assert result.data.count() == 2
        assert users == {"Bob", "Charlie"}

    def test_filters_by_end_date(self, feedbacks):
        # Should include records created before Jan 6
        request = self.mock_request({"end_date": date(2025, 1, 6).isoformat()})
        queryset = CustomerFeedback.objects.all()

        result = ListCustomerFeedbackQuery.query(queryset, request)
        users = set(result.data.values_list("user", flat=True))

        assert result.data.count() == 2
        assert users == {"Alice", "Bob"}
