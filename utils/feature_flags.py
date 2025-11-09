from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from apps.aso.models import FeatureFlag
from utils.enum import FeatureNames


def is_feature_enabled(flag_name: str, user=None):
    """
    Check if a given feature flag is enabled globally or for a specific user.

    Rules:
      ✅ If flag is enabled and no users are assigned → enabled for everyone.
      ✅ If flag is enabled and users are assigned → enabled only for those users.
      ❌ If flag is disabled or not found → disabled.
      ⚠️ If flag name not in FeatureNames → raise ImproperlyConfigured.

    Args:
        flag_name (str): The feature flag name (from FeatureNames enum).
        user (User, optional): Optional user to check against assigned users.

    Returns:
        bool: Whether the feature is enabled.
    """

    # 🔍 Validate flag name
    valid_names = FeatureNames.values()
    if flag_name not in valid_names:
        raise ImproperlyConfigured(
            f"Invalid feature name '{flag_name}' — must be one of: {valid_names}"
        )

    # 🔎 Try to fetch the feature flag
    try:
        flag = FeatureFlag.objects.prefetch_related("users").get(name=flag_name)
    except FeatureFlag.DoesNotExist:
        return None, False
    
    now = timezone.now()
    
    # # Check start_date and end_date
    # if (flag.start_date and now < flag.start_date) or (flag.end_date and now > flag.end_date):
    #     # Automatically disable expired or not yet started flags
    #     if flag.is_enabled:  # update only if still enabled
    #         flag.is_enabled = False
    #         flag.save(update_fields=['is_enabled'])
    #     return flag, False

    # Feature globally disabled
    if not flag.is_enabled:
        return flag, False

    # If no users are assigned → enabled globally
    if flag.users.count() == 0:
        return flag, True

    # If user not provided → treat as global check
    if user is None:
        return flag, True

    # If user is in assigned users → enabled
    if flag.users.filter(id=user.id).exists():
        return flag, True

    # Otherwise, disabled for this user
    return flag, False
