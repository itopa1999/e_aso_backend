from warnings import filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from apps.administrator.BLL.Commands.MarkCustomerFeedbackDone import MarkCustomerFeedbackDoneCommand
from apps.administrator.BLL.Queries.Dashboard import DashboardQuery
from apps.administrator.BLL.Queries.ListBanners import BannerListQuery
from apps.administrator.BLL.Queries.ListTransactions import TransactionListQuery
from apps.administrator.BLL.Queries.ProductList import ProductListQuery
from apps.administrator.BLL.Queries.OrderList import OrderListQuery
from apps.administrator.BLL.Queries.UserOrderList import UserListQuery
from apps.administrator.BLL.Commands.CreateCustomerFeedback import CreateCustomerFeedbackCommand
from apps.administrator.BLL.Queries.ListCustomerFeedback import ListCustomerFeedbackQuery
from apps.administrator.models import CustomerFeedback
from apps.aso.models import Product, Order
from apps.users.models import Transaction, User
from utils.Tasks.Emails.EmailForBlackFriday import send_discount_day_announcement
from utils.Tasks.Emails.EmailForProductAds import send_new_product_announcement
from utils.Tasks.Emails.EmailForRefferralDiscount import send_referral_program_announcement
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys
from utils.permissions import IsAdminPermission
from .serializers import CustomerFeedbackSerializer, DashboardSerializer, ProductSerializer, AdminOrderDetailSerializer, TransactionSerializer, UserOrderListSerializer, BulkUpdateBadgesSerializer, ProductImportSerializer
# Create your views here. 

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
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

    def get(self, request, category = None, *args, **kwargs):
        category = category or ""
        result = BannerListQuery.query(request, category)
        return Response(result.to_dict(), status=result.status_code)


class DashboardAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    serializer_class = DashboardSerializer
    # swagger_schema = TaggedAutoSchema
    def get(self, request):
        result = DashboardQuery.query(request)
        return Response(result.to_dict(), status=result.status_code)
        
        
class ProductAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    serializer_class = ProductSerializer
    # swagger_schema = TaggedAutoSchema

    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['badge']
    ordering_fields = ['current_price', 'rating', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        result = ProductListQuery.query(self.request, queryset)
        return result.data

    def get_serializer_context(self):
        return {"request": self.request}
    
    
class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = AdminOrderDetailSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated, IsAdminPermission]
    
    def get_queryset(self):        
        queryset = super().get_queryset()

        result = OrderListQuery.query(self.request, queryset)
        return result.data

    def get_serializer_context(self):
        return {"request": self.request}
   
        
        
class UserOrderListView(generics.ListAPIView):
    queryset = User.objects.prefetch_related('orders', 'groups').all()
    serializer_class = UserOrderListSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        result = UserListQuery.query(self.request,queryset)
        return result.data

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
                

class ProductBulkImportView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
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
    permission_classes = [IsAuthenticated, IsAdminPermission]
    def post(self, request):
        products_to_update = Product.objects.filter(display_product=False, is_deleted = False)
        count = products_to_update.update(display_product=True)
        return Response({"message": f"{count} products activated."}, status=status.HTTP_200_OK)
    
     
class CreateCustomerFeedbackView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    """ to create a new customer feedback"""
    serializer_class = CustomerFeedbackSerializer
    queryset = CustomerFeedback.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = CreateCustomerFeedbackCommand.execute(serializer)
        return Response(result.to_dict(), status=result.status_code)

class ListCustomerFeedbackView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    """ to list all customer feedback"""
    serializer_class = CustomerFeedbackSerializer
    
    def get_queryset(self):
        cache_key = CacheKeys.CUSTOMER_FEEDBACK_LIST
        feedbacks = GlobalCache.get(cache_key)
        if not feedbacks:
            feedbacks = CustomerFeedback.objects.all()
            GlobalCache.set(cache_key, feedbacks)
        return feedbacks

    def get(self, request, *args, **kwargs):
        feedbacks = self.get_queryset().order_by("-created_at")
        result = ListCustomerFeedbackQuery.query(feedbacks, request)
        serializer = self.get_serializer(result.data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class MarkCustomerFeedbackDoneView(APIView):
    """Mark a customer feedback as done"""
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def patch(self, request, pk):
        
        result = MarkCustomerFeedbackDoneCommand.execute(pk)
        return Response(result.to_dict(), status=result.status_code)
        

class DefTestingView(APIView):
    # permission_classes = [IsAuthenticated, IsAdminPermission]
    def get(self, request):
        result = send_new_product_announcement()
        return Response({"message": result}, status=status.HTTP_200_OK)
    
    
class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["reference", "channel", "transaction_type", "status"]
    ordering_fields = ["created_at", "amount"]
    ordering = ["-created_at"]  # newest first by default

    def list(self, request, *args, **kwargs):
        user = request.user
        base_qs = Transaction.objects.all()

        result = TransactionListQuery.query(request, base_qs)

        queryset = result.data
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        result.data = serializer.data

        if page is not None:
            return self.get_paginated_response(result.to_dict())

        return Response(result.to_dict(), status=result.status_code)



# class ResendOtpView(generics.GenericAPIView):
#     serializer_class = ResendOtpSerializer
#     permission_classes = [IsAuthenticated, IsAdminPermission]
    
#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         email = serializer.validated_data['email']
#         result = ResendOtpCommand.execute(email)
#         return Response(result.to_dict(), status=result.status_code)
    
    
    
    
# class UpdateOrderTrackingAPIView(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated, IsAdminPermission]
#     serializer_class = OrderTrackingUpdateSerializer

#     def post(self, request, *args, **kwargs):
        
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         tracking = serializer.update_status()
#         return Response({
#             "message": f"Order {tracking.order.order_number} updated to {tracking.status} successfully.",
#         }, status=status.HTTP_200_OK)
     