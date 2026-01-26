from re import search
from utils.base_result import BaseResultWithData
from django.db.models import Q
from utils.validators import safe_int  # 🔒 Safe type conversion

class UserListQuery:
    @staticmethod
    def query(request, queryset):
        
        search = request.query_params.get('search')
        
        # Apply filters dynamically with safe type conversion
        # 🔒 Use safe_int to prevent crashes on invalid numeric input
        if search:
            search_int = safe_int(search, None)
            if search_int is not None and search_int > 0:
                queryset = queryset | queryset.filter(id=search_int)
            
        if search:
            queryset = queryset.filter(
                Q(phone__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(groups__name__icontains=search)
            )
            
        return BaseResultWithData(
            data=queryset.distinct(),
            message="User list retrieved successfully.",
            status_code=200
        )