import pytest
from rest_framework.test import APIClient
from apps.administrator.models import Banner


@pytest.mark.django_db
class TestBannerListView:
    """Tests for BannerListView (banners/<str:category>/)"""

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def banners(self):
        return [
            Banner.objects.create(title="Banner 1", category="home", is_deleted=False),
            Banner.objects.create(title="Banner 2", category="sports", is_deleted=False),
            Banner.objects.create(title="Banner 3", category="news", is_deleted=False),
            Banner.objects.create(title="Deleted Banner", category="home", is_deleted=True),
        ]

    def test_get_all_banners(self, client, banners):
        """Should return all non-deleted banners when category is empty."""
        url = "/admins/api/admin/banners/"  # empty category, meaning all
        response = client.get(url)
        assert response.status_code == 200

        data = response.json().get("data", response.json())
        assert len(data) == 3
        
    def test_no_banners_for_invalid_category(self, client, banners):
        response = client.get("/admins/api/admin/banners/unknown/")
        assert response.status_code == 200
        assert response.json()["data"] == []
        

    def test_get_filtered_banners(self, client, banners):
        """Should return only banners matching 'home' category."""
        url = "/admins/api/admin/banners/home/"
        response = client.get(url)

        assert response.status_code == 200
        data = response.json().get("data", response.json())

        # only 1 banner is 'home' and not deleted
        assert len(data) == 1
        assert data[0]["category"] == "home"
        assert data[0]["title"] == "Banner 1"

    def test_multiple_categories(self, client, banners):
        """Should handle multiple categories (comma-separated)."""
        url = "/admins/api/admin/banners/home,sports/"
        response = client.get(url)

        assert response.status_code == 200
        data = response.json().get("data", response.json())
        assert len(data) == 2
        categories = {b["category"] for b in data}
        assert categories == {"home", "sports"}

    def test_uses_cached_data(self, client, mocker):
        cached = {"data": [{"title": "Cached Banner", "category": "home"}]}
        mocker.patch("utils.cache_manager.GlobalCache.get", return_value=cached)

        response = client.get("/admins/api/admin/banners/home/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data[0]["title"] == "Cached Banner"
