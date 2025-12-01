import pytest
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.aso.models import FeatureFlag
from utils.enum import FeatureNames
from utils.feature_flags import is_feature_enabled

User = get_user_model()


@pytest.mark.django_db
class TestIsFeatureEnabled:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Create users
        self.user1 = User.objects.create(email="user1@example.com")
        self.user2 = User.objects.create(email="user2@example.com")

        # Valid feature name from FeatureNames
        self.valid_flag = list(FeatureNames.values())[0]  # pick the first defined name
        
        # Date range for enabled features (start_date must be in future)
        self.now = timezone.now()
        self.start_date = self.now + timedelta(hours=1)  # 1 hour in the future
        self.end_date = self.now + timedelta(days=7)

    def test_invalid_feature_name_raises_error(self):
        with pytest.raises(ImproperlyConfigured):
            is_feature_enabled("INVALID_FEATURE")

    def test_returns_false_if_flag_does_not_exist(self):
        result = is_feature_enabled(self.valid_flag)
        assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
        flag, enabled = result
        assert enabled is False

    def test_returns_false_if_flag_disabled(self):
        FeatureFlag.objects.create(
            name=self.valid_flag, 
            is_enabled=False, 
            discount_percent=0
        )
        flag, enabled = is_feature_enabled(self.valid_flag)
        assert enabled is False

    def test_returns_true_if_enabled_globally_no_users(self):
        flag = FeatureFlag.objects.create(
            name=self.valid_flag, 
            is_enabled=True, 
            discount_percent=10,
            start_date=self.start_date,
            end_date=self.end_date
        )
        flag_obj, enabled = is_feature_enabled(self.valid_flag)
        assert enabled is True

    def test_returns_true_if_enabled_and_user_in_list(self):
        flag = FeatureFlag.objects.create(
            name=self.valid_flag, 
            is_enabled=True, 
            discount_percent=10,
            start_date=self.start_date,
            end_date=self.end_date
        )
        flag.users.add(self.user1)
        flag_obj, enabled = is_feature_enabled(self.valid_flag, user=self.user1)
        assert enabled is True

    def test_returns_false_if_enabled_and_user_not_in_list(self):
        flag = FeatureFlag.objects.create(
            name=self.valid_flag, 
            is_enabled=True, 
            discount_percent=10,
            start_date=self.start_date,
            end_date=self.end_date
        )
        flag.users.add(self.user1)
        flag_obj, enabled = is_feature_enabled(self.valid_flag, user=self.user2)
        assert enabled is False

    def test_returns_true_if_enabled_with_users_but_no_user_passed(self):
        flag = FeatureFlag.objects.create(
            name=self.valid_flag, 
            is_enabled=True, 
            discount_percent=10,
            start_date=self.start_date,
            end_date=self.end_date
        )
        flag.users.add(self.user1)
        # user=None means we check if globally accessible (rule allows True)
        flag_obj, enabled = is_feature_enabled(self.valid_flag)
        assert enabled is True
