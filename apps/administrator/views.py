from django.db.models import Q
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from apps.administrator.BLL.Queries.ListBanners import BannerListQuery
from apps.aso.models import OrderTracking, Product
from utils.permissions import IsAdminPermission
from .serializers import *
# Create your views here. 

from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from django.db.models import Sum
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from apps.administrator.serializers import BannerSerializer
from rest_framework.exceptions import AuthenticationFailed

class OptionalJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None  # No token → AnonymousUser

        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            # Invalid/expired token → Ignore, treat as anonymous
            return None
        
        
class BannerListView(generics.GenericAPIView):
    allow_any = [AllowAny]
    authentication_classes = [OptionalJWTAuthentication]    
    serializer_class = BannerSerializer

    def get(self, request, category, *args, **kwargs):
        result = BannerListQuery.query(request, category)
        return Response(result.to_dict(), status=result.status_code)


class DashboardAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    serializer_class = DashboardSerializer
    # swagger_schema = TaggedAutoSchema
    def get(self, request):
        
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        
        # --- Current Month Counts ---
        products_current = Product.objects.filter(created_at__gte=current_month_start, is_deleted = False).count()
        orders_current = Order.objects.filter(created_at__gte=current_month_start, is_deleted = False).count()
        customers_current = Order.objects.filter(created_at__gte=current_month_start, is_deleted = False).values('user').distinct().count()

        # --- Last Month Counts ---
        products_last = Product.objects.filter(created_at__gte=last_month_start, created_at__lte=last_month_end, is_deleted = False).count()
        orders_last = Order.objects.filter(created_at__gte=last_month_start, created_at__lte=last_month_end, is_deleted = False).count()
        customers_last = Order.objects.filter(created_at__gte=last_month_start, created_at__lte=last_month_end, is_deleted = False).values('user').distinct().count()

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
                "value": Product.objects.filter(is_deleted=False).count(),
                **calculate_change(products_current, products_last),
            },
            "total_orders": {
                "value": Order.objects.filter(is_deleted=False).count(),
                **calculate_change(orders_current, orders_last),
            },
            "total_customers": {
                "value": Order.objects.values('user').distinct().count(),
                **calculate_change(customers_current, customers_last),
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
            {"product": OrderItem.objects.filter(product_id=item['product'], is_deleted = False).first().product, "sold_count": item['sold_count']}
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
                
        
        # --- Response ---
        return Response({
            "stats": status_data,
            "order_status": order_stats,
            "top_products": top_products_serialized,
            "recent_orders": recent_orders_serialized,
        })
        
        
        
class ProductAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    serializer_class = ProductSerializer
    # swagger_schema = TaggedAutoSchema

    queryset = Product.objects.filter(display_product=True, is_deleted = False)
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['badge']
    ordering_fields = ['current_price', 'rating', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Extract query parameters
        max_price = self.request.query_params.get('max_price')
        min_price = self.request.query_params.get('min_price')
        rating = self.request.query_params.get('rating')
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category')

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

        return queryset

    def get_serializer_context(self):
        return {"request": self.request}
    
    
    

class OrderListView(generics.ListAPIView):
    queryset = Order.objects.filter(is_deleted = False)
    serializer_class = AdminOrderDetailSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated, IsAdminPermission]
    
    def get_queryset(self):        
        queryset = super().get_queryset()

        # Extract query parameters

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )

        if queryset is None:
            queryset = queryset.filter(id=search)
        return queryset

    def get_serializer_context(self):
        return {"request": self.request}
    
    

class UpdateOrderTrackingAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    serializer_class = OrderTrackingUpdateSerializer

    def post(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tracking = serializer.update_status()
        return Response({
            "message": f"Order {tracking.order.order_number} updated to {tracking.status} successfully.",
        }, status=status.HTTP_200_OK)
        
        
        
class UserOrderListView(generics.ListAPIView):
    queryset = User.objects.prefetch_related('orders', 'groups').all()
    serializer_class = UserOrderListSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    
    def get_queryset(self):
        
        queryset = super().get_queryset()

        # Extract query parameters

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(phone__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(groups__name__icontains=search)
            )

        if queryset is None:
            queryset = queryset.filter(id=search)
        return queryset.distinct()







from django.db import transaction



class BulkUpdateProductBadgesView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    serializer_class = BulkUpdateBadgesSerializer
    
    def patch(self, request):
        """
        Bulk update product badges
        Body: {
            "badge": "New",
            "product_ids": [1, 2, 3],
            "product_titles": ["Product A", "Product B"]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        badge = validated_data['badge']
        product_ids = validated_data.get('product_ids', [])
        product_titles = validated_data.get('product_titles', [])
                
        try:
            with transaction.atomic():
                updated_count = 0
                
                # Update by IDs
                if product_ids:
                    count_by_id = Product.objects.filter(
                        id__in=product_ids, is_deleted = False
                    ).update(badge=badge)
                    updated_count += count_by_id
                
                # Update by titles
                if product_titles:
                    count_by_title = Product.objects.filter(
                        title__in=product_titles, is_deleted = False
                    ).update(badge=badge)
                    updated_count += count_by_title
                
                return Response({
                    "message": f"Successfully updated badges for {updated_count} products",
                    "badge": badge,
                    "updated_count": updated_count
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {"error": f"An error occurred during update: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductBulkImportView(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated, IsAdminPermission]
    serializer_class = ProductImportSerializer
    def post(self, request):
        if not isinstance(request.data, list):
            return Response({'error': 'Data must be a list of products'}, status=status.HTTP_400_BAD_REQUEST)

        created_count = 0
        errors = []

        for idx, item in enumerate(request.data):
            serializer = ProductImportSerializer(data=item)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append({
                    "index": idx,
                    "errors": serializer.errors
                })

        return Response({
            "message": "Import finished",
            "products_created": created_count,
            "errors": errors
        }, status=status.HTTP_200_OK)
        
        
class ActivateProductsAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsAdminPermission]
    def post(self, request):
        products_to_update = Product.objects.filter(display_product=False, is_deleted = False)
        count = products_to_update.update(display_product=True)
        return Response({"message": f"{count} products activated."}, status=status.HTTP_200_OK)
    
     

class ResendOtpView(generics.GenericAPIView):
    serializer_class = ResendOtpSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        result = ResendOtpCommand.execute(email)
        return Response(result.to_dict(), status=result.status_code)