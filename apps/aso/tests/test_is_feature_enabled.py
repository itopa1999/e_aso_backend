import pytest
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import get_user_model
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

    def test_invalid_feature_name_raises_error(self):
        with pytest.raises(ImproperlyConfigured):
            is_feature_enabled("INVALID_FEATURE")

    def test_returns_false_if_flag_does_not_exist(self):
        assert is_feature_enabled(self.valid_flag) is False

    def test_returns_false_if_flag_disabled(self):
        FeatureFlag.objects.create(name=self.valid_flag, is_enabled=False)
        assert is_feature_enabled(self.valid_flag) is False

    def test_returns_true_if_enabled_globally_no_users(self):
        flag = FeatureFlag.objects.create(name=self.valid_flag, is_enabled=True)
        assert is_feature_enabled(self.valid_flag) is True

    def test_returns_true_if_enabled_and_user_in_list(self):
        flag = FeatureFlag.objects.create(name=self.valid_flag, is_enabled=True)
        flag.users.add(self.user1)
        assert is_feature_enabled(self.valid_flag, user=self.user1) is True

    def test_returns_false_if_enabled_and_user_not_in_list(self):
        flag = FeatureFlag.objects.create(name=self.valid_flag, is_enabled=True)
        flag.users.add(self.user1)
        assert is_feature_enabled(self.valid_flag, user=self.user2) is False

    def test_returns_true_if_enabled_with_users_but_no_user_passed(self):
        flag = FeatureFlag.objects.create(name=self.valid_flag, is_enabled=True)
        flag.users.add(self.user1)
        # user=None means we check if globally accessible (rule allows True)
        assert is_feature_enabled(self.valid_flag) is True
