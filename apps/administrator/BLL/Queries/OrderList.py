from utils.base_result import BaseResultWithData
from django.db.models import Q

class OrderListQuery:
    @staticmethod
    def query(request, queryset):
        # Extract query parameters
        search = request.query_params.get('search')
        
        # Apply filters dynamically
        if search and search.isdigit():
            queryset = queryset | queryset.filter(id=int(search))
            
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )

        return BaseResultWithData(
            data=queryset,
            message="Order list retrieved successfully.",
            status_code=200
        )
