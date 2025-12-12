from http import HTTPStatus
from apps.aso.models import Order
from apps.aso.serializers import OrderSerializer
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys
from django.core.paginator import Paginator

class UserOrderListQuery:

    @staticmethod
    def query(request):
        user = request.user
        page = request.query_params.get('page', 1)
        page_size = 20  # 20 orders per page
        
        cache_key = CacheKeys.format(CacheKeys.USER_ORDERS, user_id=user.id)

        # ✅ Try cache first
        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            return BaseResultWithData(
                data=cached_data["data"],
                status_code=HTTPStatus.OK,
                message="User orders fetched successfully"
            )
            
        orders = Order.objects.filter(user=user, is_deleted=False).prefetch_related('items', 'tracking_events').order_by('-created_at')
        
        # Paginate results
        paginator = Paginator(orders, page_size)
        
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)
        
        serializer = OrderSerializer(page_obj.object_list, many=True, context={'request': request})
        
        # Build response with pagination info
        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "next": f"?page={page_obj.next_page_number()}" if page_obj.has_next() else None,
            "previous": f"?page={page_obj.previous_page_number()}" if page_obj.has_previous() else None,
        }
        
        GlobalCache.set(cache_key, {"data": response_data})
        
        return BaseResultWithData(
            data=response_data,
            status_code=HTTPStatus.OK,
            message="User orders fetched successfully"
        )
