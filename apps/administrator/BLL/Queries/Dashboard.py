from datetime import timedelta
from http import HTTPStatus
from click import group
from django.utils import timezone
from django.db.models import Sum, Count

from apps.aso.models import OrderTracking, Product, Order, OrderItem
from apps.administrator.serializers import (
    DashboardOrderSerializer,
    DashboardTopProductSerializer,
)
from apps.users.models import User
from utils.base_result import BaseResultWithData
from utils.enum import GroupNames

class DashboardQuery:
    @staticmethod
    def query(request):
        
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        
        # --- Current Month Counts ---
        products_current = Product.objects.filter(created_at__gte=current_month_start).count()
        orders_current = Order.objects.filter(created_at__gte=current_month_start).count()
        customers_current = Order.objects.filter(created_at__gte=current_month_start).values('user').distinct().count()
        users_current = User.objects.filter(created_at__gte=current_month_start, groups__name=GroupNames.CUSTOMER.value).count()
        riders_current = User.objects.filter(created_at__gte=current_month_start, groups__name=GroupNames.RIDER.value).count()

        # --- Last Month Counts ---
        products_last = Product.objects.filter(created_at__gte=last_month_start, created_at__lte=last_month_end).count()
        orders_last = Order.objects.filter(created_at__gte=last_month_start, created_at__lte=last_month_end).count()
        customers_last = Order.objects.filter(created_at__gte=last_month_start, created_at__lte=last_month_end).values('user').distinct().count()
        users_last = User.objects.filter(created_at__gte=last_month_start, created_at__lte=last_month_end, groups__name=GroupNames.CUSTOMER.value).count()
        riders_last = User.objects.filter(created_at__gte=last_month_start, created_at__lte=last_month_end, groups__name=GroupNames.RIDER.value).count()
        
        def calculate_change(current, last):
            if last == 0 and current == 0:
                return {"change": "0%", "direction": "no change"}
            if last == 0:
                return {"change": "+100%", "direction": "up"}
            percent_change = ((current - last) / last) * 100
            direction = "up" if percent_change >= 0 else "down"
            return {"change": f"{abs(percent_change):.2f}%", "direction": direction}
        
        order_stats = {
            "total_products": {
                "value": Product.objects.count(),
                **calculate_change(products_current, products_last),
            },
            "total_orders": {
                "value": Order.objects.count(),
                **calculate_change(orders_current, orders_last),
            },
            "total_customers": {
                "value": Order.objects.values('user').distinct().count(),
                **calculate_change(customers_current, customers_last),
            },
            "total_users": {
                "value": User.objects.filter(groups__name=GroupNames.CUSTOMER.value).count(),
                **calculate_change(users_current, users_last),
            },
            "total_riders": {
                "value": User.objects.filter(groups__name=GroupNames.RIDER.value).count(),
                **calculate_change(riders_current, riders_last),
            },
        }
        
        # --- Top Products ---
        top_products_qs = (
            OrderItem.objects
            .select_related('product')
            .values('product', 'product__title')
            .annotate(sold_count=Sum('quantity'))
            .order_by('-sold_count')[:10]
        )

        top_products_data = [
            {"product": OrderItem.objects.filter(product_id=item['product']).first().product, "sold_count": item['sold_count']}
            for item in top_products_qs
        ]

        top_products_serialized = DashboardTopProductSerializer(top_products_data, many=True).data

        # Stats
        stats = (
            OrderTracking.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )

        # Convert to desired format (name and value)
        status_data = [
            {
                "name": dict(OrderTracking.STATUS_CHOICES).get(stat['status'], stat['status']),
                "value": stat['count']
            }
            for stat in stats
        ]
        
        # Recent orders
        recent_orders = Order.objects.filter(is_deleted = False)[:10]
        recent_orders_serialized = DashboardOrderSerializer(recent_orders, many=True).data
                
        
        return BaseResultWithData(
            data={
                "stats": status_data,
                "order_status": order_stats,
                "top_products": top_products_serialized,
                "recent_orders": recent_orders_serialized,
            },
            status_code=HTTPStatus.OK,
            message="Dashboard data fetched successfully."
        )