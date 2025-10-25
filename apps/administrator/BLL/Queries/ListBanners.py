

from http import HTTPStatus
from apps.administrator.models import Banner
from apps.administrator.serializers import BannerSerializer
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys


class BannerListQuery:
    @staticmethod
    def query(request, category_str):
        categories = [c.strip() for c in category_str.split(",") if c.strip()]
        cache_key = CacheKeys.format(CacheKeys.BANNER, category="_".join(categories))

        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            print("from cache")
            return BaseResultWithData(
                data=cached_data["data"],
                status_code=HTTPStatus.OK,
                message="banner details fetched successfully"
            )
            
        try:
            if categories:
                banners = Banner.objects.filter(category__in=categories, is_deleted=False)
            else:
                banners = Banner.objects.filter(is_deleted=False)
            
            serializer = BannerSerializer(banners, many=True, context={'request': request})
            
            GlobalCache.set(cache_key, {"data": serializer.data})
            return BaseResultWithData(
                data=serializer.data,
                status_code=HTTPStatus.OK,
                message="banners retrieved successfully."
            )
        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to banners lookups: {str(e)}"
            )