from re import search
from utils.base_result import BaseResultWithData
from django.db.models import Q
class UserListQuery:
    @staticmethod
    def query(request, queryset):
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(phone__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(groups__name__icontains=search)
            )

        if search and search.isdigit():
            queryset = queryset | queryset.filter(id=int(search))
            
        return BaseResultWithData(
            data=queryset.distinct(),
            message="User list retrieved successfully.",
            status_code=200
        )