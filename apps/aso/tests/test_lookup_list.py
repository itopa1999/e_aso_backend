# apps/aso/tests/test_lookup_list_query.py
import pytest
from apps.aso.BBL.Queries.LookUpList import LookUpListQuery
from apps.aso.models import LookUp
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys

@pytest.mark.django_db
class TestLookUpListQuery:

    @pytest.fixture(autouse=True)
    def setup(self):
        GlobalCache.clear()
        self.lookup1 = LookUp.objects.create(name="Category1", is_deleted=False)
        self.lookup2 = LookUp.objects.create(name="Category2", is_deleted=False)
        self.deleted_lookup = LookUp.objects.create(name="Deleted", is_deleted=True)

    def test_query_returns_all_non_deleted_lookups(self):
        result = LookUpListQuery.query()
        assert result.status_code == 200
        assert set(result.data) == {self.lookup1, self.lookup2}
        assert self.deleted_lookup not in result.data

    def test_query_uses_cache_if_available(self):
        cache_key = CacheKeys.LOOKUP
        cache_data = {"data": ["cached_item"]}
        GlobalCache.set(cache_key, cache_data)

        result = LookUpListQuery.query()
        assert result.data == ["cached_item"]
        assert result.status_code == 200
