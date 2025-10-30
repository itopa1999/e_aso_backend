from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Avg, F
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from apps.aso.models import Cart, Order, Product, ShippingAddress
from .utils import apply_date_category_filters
from rest_framework.permissions import IsAuthenticated
from utils.permissions import IsAdminPermission

from django.db.models import Count

class RevenueOverTimeAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def get(self, request):
        period = request.query_params.get("period", "day")
        truncate = {"day": TruncDate, "week": TruncWeek, "month": TruncMonth}.get(period, TruncDate)

        queryset = apply_date_category_filters(Order.objects.all(), request)

        data = (
            queryset.annotate(period=truncate("created_at"))
            .values("period")
            .annotate(total_revenue=Sum("total"))
            .order_by("period")
        )

        return Response(data)
    
    
    
class OrdersPerDayAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    def get(self, request):
        queryset = apply_date_category_filters(Order.objects.all(), request)

        data = (
            queryset.annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(total_orders=Count("id"))
            .order_by("date")
        )
        return Response(data)
    
    
    
class CategorySalesAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    def get(self, request):
        queryset = apply_date_category_filters(Order.objects.all(), request)

        data = (
            queryset.values("items__product__category__name")
            .annotate(total_sales=Sum("total"))
            .order_by("-total_sales")
        )
        return Response(data)
    
    
    
class TopProductsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    def get(self, request):
        queryset = apply_date_category_filters(Order.objects.all(), request)

        data = (
            queryset.values("items__product__title")
            .annotate(total_sold=Sum("items__quantity"), total_revenue=Sum("items__price"))
            .order_by("-total_sold")[:10]
        )
        return Response(data)
    


class CustomerInsightsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    def get(self, request):
        queryset = apply_date_category_filters(Order.objects.all(), request)

        all_customers = queryset.values_list("user_id", flat=True).distinct()
        returning = [
            u for u in all_customers
            if Order.objects.filter(user_id=u).count() > 1
        ]
        new = set(all_customers) - set(returning)

        return Response({
            "new_customers": len(new),
            "returning_customers": len(returning),
        })
        
        

class TopBuyersAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    def get(self, request):
        queryset = apply_date_category_filters(Order.objects.all(), request)

        data = (
            queryset.values("user__email")
            .annotate(total_spent=Sum("total"), orders=Count("id"))
            .order_by("-total_spent")[:10]
        )
        return Response(data)
    
    

class CustomerLocationsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    def get(self, request):
        queryset = ShippingAddress.objects.select_related("order__user")
        queryset = apply_date_category_filters(queryset, request)

        data = (
            queryset.values("city", "state")
            .annotate(total_customers=Count("order__user", distinct=True))
            .order_by("-total_customers")
        )
        return Response(data)
    
    

class CustomerMetricsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    def get(self, request):
        queryset = apply_date_category_filters(Order.objects.all(), request)

        avg_order_value = queryset.aggregate(avg=Avg("total"))["avg"] or 0

        total_carts = Cart.objects.count()
        converted_carts = Cart.objects.filter(user__orders__isnull=False).distinct().count()
        cart_abandonment_rate = (
            (1 - (converted_carts / total_carts)) * 100 if total_carts else 0
        )

        return Response({
            "avg_order_value": avg_order_value,
            "cart_abandonment_rate": round(cart_abandonment_rate, 2),
        })



class MostViewedProductsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]   
    def get(self, request):
        queryset = apply_date_category_filters(Product.objects.all(), request)

        data = (
            queryset.values("title")
            .annotate(total_views=Sum("reviews_count"))  # assuming you track views
            .order_by("-total_views")[:10]
        )
        return Response(data)
    
    

class TopRatedProductsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    def get(self, request):
        queryset = apply_date_category_filters(Product.objects.all(), request)
        data = queryset.values("title", "rating").order_by("-rating")[:10]
        return Response(data)
    
    
    
class FulfillmentStatsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    def get(self, request):
        queryset = apply_date_category_filters(Order.objects.all(), request)

        data = {
            "pending": queryset.filter(tracking_events__status="placed").count(),
            "completed": queryset.filter(tracking_events__status="delivered").count(),
            "cancelled": queryset.filter(tracking_events__status="cancelled").count(),
            "avg_delivery_days": queryset.exclude(
                delivery_date__isnull=True, estimated_delivery_date__isnull=True
            ).annotate(
                diff=F("delivery_date") - F("created_at")
            ).aggregate(avg=Avg("diff"))["avg"],
        }
        return Response(data)