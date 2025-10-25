from http import HTTPStatus
from apps.aso.models import LookUp
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys


class LookUpListQuery:
    @staticmethod
    def query():
        cache_key = CacheKeys.LOOKUP

        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            return BaseResultWithData(
                data=cached_data["data"],
                status_code=HTTPStatus.OK,
                message="Order details fetched successfully"
            )
            
        try:
            lookups = LookUp.objects.filter(is_deleted=False)
            
            GlobalCache.set(cache_key, {"data": lookups})
            return BaseResultWithData(
                data=lookups,
                status_code=HTTPStatus.OK,
                message="Lookups retrieved successfully."
            )
        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to fetch lookups: {str(e)}"
            )
