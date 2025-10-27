

from utils.enum import FeatureNames
from utils.feature_flags import is_feature_enabled


def unset_limited_product():

    if not is_feature_enabled(FeatureNames.PRODUCT_LIMITATION.value):
        return "⚠️ Limited product feature is disabled."