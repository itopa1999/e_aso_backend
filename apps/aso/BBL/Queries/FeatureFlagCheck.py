from http import HTTPStatus
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys
from utils.feature_flags import is_feature_enabled

class FeatureFlagCheck:
    @staticmethod
    def query(feature_name):
        cache_key = CacheKeys.format(CacheKeys.FEATURE_FLAGS, feature_name=feature_name)
        cached_data = GlobalCache.get(cache_key)
        if cached_data is not None: 
            return BaseResultWithData(
                data=cached_data["data"],
                status_code=HTTPStatus.OK,
                message=f"Feature flag '{feature_name}' status retrieved successfully from cache."
            )
        flag, enabled = is_feature_enabled(feature_name)
        GlobalCache.set(cache_key, {"data": enabled})
        return BaseResultWithData(
            data=enabled,
            status_code=HTTPStatus.OK,
            message=f"Feature flag '{feature_name}' status retrieved successfully."
        )
