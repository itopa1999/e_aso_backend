from utils.base_result import BaseResultWithData
from django.db.models import Q

class ProductListQuery:
    @staticmethod
    def query(request, queryset):
        
        # Extract query parameters
        max_price = request.query_params.get('max_price')
        min_price = request.query_params.get('min_price')
        rating = request.query_params.get('rating')
        search = request.query_params.get('search')
        category = request.query_params.get('category')

        # Apply filters dynamically
        if min_price:
            queryset = queryset.filter(current_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(current_price__lte=max_price)
        if rating:
            queryset = queryset.filter(rating__gte=rating)
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
            