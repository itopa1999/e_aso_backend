from utils.base_result import BaseResultWithData
from django.db.models import Q
from utils.validators import safe_float, safe_int

class ProductListQuery:
    @staticmethod
    def query(request, queryset):
        
        # Extract query parameters
        if hasattr(request, "query_params"):
            params = request.query_params
        elif hasattr(request, "GET"):
            params = request.GET
        else:
            params = {}

        max_price = params.get("max_price")
        min_price = params.get("min_price")
        rating = params.get("rating")
        search = params.get("search")
        category = params.get("category")

        if min_price:
            min_price_float = safe_float(min_price, None)
            if min_price_float is not None:
                queryset = queryset.filter(current_price__gte=min_price_float)
        
        if max_price:
            max_price_float = safe_float(max_price, None)
            if max_price_float is not None:
                queryset = queryset.filter(current_price__lte=max_price_float)
        
        # 🔒 Use safe_int for rating with default 0
        if rating:
            rating_int = safe_int(rating, 0)
            if rating_int > 0:
                queryset = queryset.filter(rating__gte=rating_int)
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(product_number__icontains=search) |
                Q(category__name__icontains=search)
            )

        return BaseResultWithData(
            data=queryset,
            message="Product list retrieved successfully.",
            status_code=200
        )
            