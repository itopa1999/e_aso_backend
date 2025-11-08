

from utils.enum import FeatureNames
from utils.feature_flags import is_feature_enabled


def unset_limited_product():

    flag, enable = is_feature_enabled(FeatureNames.PRODUCT_LIMITATION.value)
    if not enable:
        return "⚠️ Limited product feature is disabled."