from django.db.models import Q
from http import HTTPStatus
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys


class ProductListQuery:
    @staticmethod
    def query(params, queryset):
            
        max_price = params.get("max_price")
        min_price = params.get("min_price")
        rating = params.get("rating")
        search = params.get("search")
        cat = params.get("category")

        if min_price:
            queryset = queryset.filter(current_price__gte=min_price)

        if max_price:
            queryset = queryset.filter(current_price__lte=max_price)

        if rating:
            queryset = queryset.filter(rating=rating)

        if cat:
            queryset = queryset.filter(category__name__icontains=cat)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(product_number__icontains=search)
                | Q(category__name__icontains=search)
            )
            
        return BaseResultWithData(
            data=queryset,
            status_code=HTTPStatus.OK,
            message="Products fetched successfully."
        )




