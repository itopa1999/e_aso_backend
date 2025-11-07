import pytest
from types import SimpleNamespace
from datetime import datetime
from django.utils import timezone
from apps.administrator.BLL.Queries.ListTransactions import TransactionListQuery
from apps.users.models import Transaction, User
from utils.base_result import BaseResultWithData

@pytest.mark.django_db
class TestTransactionListQuery:
    """Unit tests for TransactionListQuery"""

    @pytest.fixture
    def transactions(self):
        user = User.objects.create_user(email="test@example.com", password="password123")
        base_dates = [
            timezone.make_aware(datetime(2025, 1, 1)),  # Alice
            timezone.make_aware(datetime(2025, 1, 5)),  # Bob
            timezone.make_aware(datetime(2025, 1, 10)), # Charlie
        ]

        t1 = Transaction.objects.create(
            user=user, amount=100, transaction_type="PAYMENT",
            reference="REF001", channel="CARD", status="SUCCESS"        )
        t2 = Transaction.objects.create(
            user=user, amount=200, transaction_type="PAYMENT",
            reference="REF002", channel="CARD", status="SUCCESS"        )
        t3 = Transaction.objects.create(
            user=user, amount=300, transaction_type="PAYMENT",
            reference="REF003", channel="CARD", status="SUCCESS"        )
        
        Transaction.objects.filter(pk=t1.pk).update(created_at=base_dates[0])
        Transaction.objects.filter(pk=t2.pk).update(created_at=base_dates[1])
        Transaction.objects.filter(pk=t3.pk).update(created_at=base_dates[2])
        
        return [t1, t2, t3]

    def mock_request(self, params):
        """Mocks a DRF request object with query_params"""
        return SimpleNamespace(query_params=params)

    def test_query_returns_all_transactions_without_filters(self, transactions):
        """Should return all transactions when no filters are applied"""
        request = self.mock_request({})
        queryset = Transaction.objects.all()
        result = TransactionListQuery.query(request, queryset)
        assert isinstance(result, BaseResultWithData)
        assert result.status_code == 200
        assert result.data.count() == len(transactions)

    def test_query_filters_transactions_by_start_date(self, transactions):
        """Should return only transactions after the given start date"""
        start_date = datetime(2025, 1, 3).date().isoformat()
        request = self.mock_request({"start_date": start_date})
        queryset = Transaction.objects.all()
        result = TransactionListQuery.query(request, queryset)
        ids = set(result.data.values_list("id", flat=True))
        assert result.data.count() == 2
        assert ids == {transactions[1].id, transactions[2].id}

    def test_query_filters_transactions_by_end_date(self, transactions):
        """Should return only transactions before the given end date"""
        end_date = datetime(2025, 1, 6).date().isoformat()
        request = self.mock_request({"end_date": end_date})
        queryset = Transaction.objects.all()
        result = TransactionListQuery.query(request, queryset)
        ids = set(result.data.values_list("id", flat=True))
        assert result.data.count() == 2
        assert ids == {transactions[0].id, transactions[1].id}

    def test_query_filters_transactions_by_date_range(self, transactions):
        """Should return only transactions within the given start and end date range"""
        start_date = datetime(2025, 1, 2).date().isoformat()
        end_date = datetime(2025, 1, 9).date().isoformat()
        request = self.mock_request({"start_date": start_date, "end_date": end_date})
        queryset = Transaction.objects.all()
        result = TransactionListQuery.query(request, queryset)
        ids = set(result.data.values_list("id", flat=True))
        assert result.data.count() == 1
        assert ids == {transactions[1].id}
