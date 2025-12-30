from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from apps.aso.BBL.Commands.Cart.AddToCart import AddToCartCommand
from apps.aso.BBL.Commands.Cart.DeleteAllCartsItems import DeleteAllCartItemsCommand
from apps.aso.BBL.Commands.Cart.MoveAllToCart import MoveAllToCartCommand
from apps.aso.BBL.Commands.Cart.RemoveCartItem import RemoveCartItemCommand
from apps.aso.BBL.Commands.Cart.UpdateCartDesc import UpdateCartDescCommand
from apps.aso.BBL.Commands.Cart.UpdateCartQuantity import UpdateCartQuantityCommand
from apps.aso.BBL.Commands.Cart.UpdateCartState import UpdateCartStateCommand
from apps.aso.BBL.Commands.Watchlist.RemoveAllWatchlist import RemoveAllWatchlistCommand
from apps.aso.BBL.Commands.Cart.ReorderItems import ReorderItemsCommand
from apps.aso.BBL.Commands.Watchlist.ToggleWatchlist import ToggleWatchlistCommand
from apps.aso.BBL.Commands.Cart.PlaceOrder import PlaceOrderCommand
from apps.aso.BBL.Commands.RecentSearch.AddRecentSearch import AddRecentSearchCommand
from apps.aso.BBL.Commands.RecentSearch.DeleteRecentSearch import DeleteRecentSearchCommand, DeleteAllRecentSearchesCommand
from apps.aso.BBL.Queries.Cart.GetCartDetails import GetCartDetailQuery
from apps.aso.BBL.Queries.Cart.PaystackConfirm import PaystackConfirmQuery
from apps.aso.BBL.Queries.Cart.FlutterConfirm import FlutterwaveConfirmQuery
from apps.aso.BBL.Queries.CartAndWatchlistCount import CartAndWatchlistCountQuery
from apps.aso.BBL.Queries.FeatureFlagCheck import FeatureFlagCheck
from apps.aso.BBL.Queries.LookUpList import LookUpListQuery
from apps.aso.BBL.Queries.Order.TrackingDetails import TrackingDetailsQuery
from apps.aso.BBL.Queries.Product.LimitedProducts import LimitedProductsQuery
from apps.aso.BBL.Queries.Product.ProductDetails import ProductDetailQuery
from apps.aso.BBL.Queries.Watchlist.GetWatchlistProducts import GetWatchlistProductsQuery
from apps.aso.BBL.Queries.Order.OrderDetails import OrderDetailQuery
from apps.aso.BBL.Queries.Order.UserOrderList import UserOrderListQuery
from apps.aso.BBL.Queries.Product.ProductList import ProductListQuery
from apps.aso.BBL.Queries.RecentSearch.GetRecentSearches import GetRecentSearchesQuery
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys
from utils.permissions import IsCustomerPermission
from .models import *
from .serializers import *
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from .deliveryFee import delivery_fees
from apps.aso.flutterwave import validate as flutterwave_validate
# Create your views here.

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

class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]

    def get(self, request):
        result = UserOrderListQuery.query(self.request)
        return Response(result.to_dict(), status=result.status_code)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema

    def get(self, request, pk):
        result = OrderDetailQuery.query(self.request, pk)
        return Response(result.to_dict(), status=result.status_code)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    

class TrackingDetailsView(generics.RetrieveAPIView):
    serializer_class = OrderTrackingDetailsSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema

    def get(self, request, order_id):
        
        result = TrackingDetailsQuery.query(request.user, order_id)
        return Response(result.to_dict(), status=result.status_code)
        
    
    
class ReorderItemsView(generics.GenericAPIView):
    serializer_class = AddToCartCountResponseSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema

    def post(self, request):
        order_id = request.GET.get("order_id")
        result = ReorderItemsCommand.execute(request.user, order_id)
        return Response(result.to_dict(), status=result.status_code)
    


class WatchlistProductsView(generics.ListAPIView):
    serializer_class = WatchlistProductSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema

    def get(self, request):
        result = GetWatchlistProductsQuery.query(request.user, request)
        return Response(result.to_dict(), status=result.status_code)
    
    def get_serializer_context(self):
        return {"request": self.request}
    

class ToggleWatchlistView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema
    def put(self, request, product_id):
        result = ToggleWatchlistCommand.execute(request.user, product_id)
        return Response(result.to_dict(), status=result.status_code)
        

class RemoveAllWatchlistView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema

    def delete(self, request):
        result = RemoveAllWatchlistCommand.execute(request.user)
        return Response(result.to_dict(), status=result.status_code)
    
class MoveAllToCartView(generics.GenericAPIView):
    serializer_class = AddToCartCountResponseSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema

    def post(self, request):
        result = MoveAllToCartCommand.execute(request.user)
        return Response(result.to_dict(), status=result.status_code)
    
    
class AddToCartView(generics.GenericAPIView):
    serializer_class = AddToCartCountResponseSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema

    def post(self, request):
        result = AddToCartCommand.execute(
            user=request.user,
            product_id=request.GET.get("product_id"),
            quantity=request.GET.get("quantity"),
            desc=request.data.get("desc", "{}")
        )
        return Response(result.to_dict(), status=result.status_code)
    
class CartDetailAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    serializer_class = CartDetailSerializer
    # swagger_schema = TaggedAutoSchema

    def get(self, request, *args, **kwargs):
        result = GetCartDetailQuery.query(request)
        return Response(result.to_dict(), status=result.status_code)

        

class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    serializer_class = UpdateQuantitySerializer
    # swagger_schema = TaggedAutoSchema 
    
    def patch(self, request):
        serializer = UpdateQuantitySerializer(data=request.data)
        result = UpdateCartQuantityCommand.execute(request.user, serializer)
        return Response(result.to_dict(), status=result.status_code)
    
    
class UpdateCartDescView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    serializer_class = UpdateDescSerializer
    # swagger_schema = TaggedAutoSchema 
    
    def patch(self, request):
        serializer = UpdateDescSerializer(data=request.data)
        result = UpdateCartDescCommand.execute(request.user, serializer)
        return Response(result.to_dict(), status=result.status_code)


class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    serializer_class = DeleteItemFromCartSerializer
    # swagger_schema = TaggedAutoSchema
    
    def delete(self, request):
        serializer = DeleteItemFromCartSerializer(data=request.data)
        result = RemoveCartItemCommand.execute(request.user, serializer)
        return Response(result.to_dict(), status=result.status_code)

class UpdateCartStateView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]

    def post(self, request):
        state = request.data.get("state")

        result = UpdateCartStateCommand.execute(request.user, state)
        return Response(result.to_dict(), status=result.status_code)
    
    
class ClearCartView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]

    def delete(self, request):
        """Delete all cart items for the authenticated user."""
        user = request.user
        
        result = DeleteAllCartItemsCommand.execute(user)
        return Response(result.to_dict(), status=result.status_code)
        
   
class PlaceOrderView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShippingInfoSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data.get("shipping_info"))
        serializer.is_valid(raise_exception=True)
        shipping_data = serializer.validated_data        
        
        result = PlaceOrderCommand.execute(request, shipping_data)

        return Response(result.to_dict(), status=result.status_code)
        
        
class PaystackConfirmSubscriptionView(APIView):
    def get(self, request, reference, *args, **kwargs):
        return PaystackConfirmQuery.execute(reference)


class MonnifyConfirmView(APIView):
    """Handle Monnify payment confirmation"""
    def get(self, request, reference, *args, **kwargs):
        # TODO: Implement Monnify validation
        return Response(
            {
                "status": "pending",
                "message": "Monnify payment confirmation - Implementation in progress",
                "reference": reference,
                "gateway": "monnify"
            },
            status=status.HTTP_200_OK
        )


class FlutterwaveConfirmView(APIView):
    """Handle Flutterwave payment confirmation"""
    def get(self, request, reference, *args, **kwargs):
        return FlutterwaveConfirmQuery.execute(reference)


class ProductListView(generics.ListAPIView):
    # queryset = Product.objects.filter(display_product = True, is_deleted = False)
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]
    serializer_class = WatchlistProductSerializer
    # swagger_schema = TaggedAutoSchema
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['badge']
    ordering_fields = ['current_price', 'rating', 'created_at']
    
    def get_queryset(self):
        cache_key = CacheKeys.PRODUCT_LIST

        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            queryset = cached_data
        else:
            queryset = Product.objects.filter(display_product = True, is_deleted = False).distinct()
            GlobalCache.set(cache_key, queryset)
            
        result = ProductListQuery.query(self.request.query_params, queryset)
        if result.status_code == status.HTTP_200_OK:
            return result.data
        return Product.objects.none()
        

    
    def get_serializer_context(self):
        return {"request": self.request}
    
    
    
class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailFullSerializer
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_object(self):
        result = ProductDetailQuery.query(self.kwargs["id"])
        if result.status_code != status.HTTP_200_OK:
            raise Product.DoesNotExist
        return result.data

    
    

class CartAndWatchlistCountView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    serializer_class = CartAndWatchlistCountSerializer
    # swagger_schema = TaggedAutoSchema
    
    def get(self, request):
        result = CartAndWatchlistCountQuery.query(request.user)
        return Response(result.data, status=result.status_code)
    
    
class LookUpView(APIView):
    serializer_class = LookUpsSerializer
    allow_any = [AllowAny]
    authentication_classes = [OptionalJWTAuthentication]

    # @swagger_auto_schema(tags=["Categories"])
    # swagger_schema = TaggedAutoSchema
    def get(self, request):
        result = LookUpListQuery.query()
        serializer = self.serializer_class(result.data, many=True)
        return Response(serializer.data, status=result.status_code)
    
        
class DeliveryFeeAPIView(APIView):
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"delivery_fees": delivery_fees})
    
    
class CheckFeatureFlagView(APIView):
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]
    
    

    def get(self, request, feature_name):
        result = FeatureFlagCheck.query(feature_name)
        return Response(result.to_dict(), status=result.status_code)


class LimitedProductsView(APIView):
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        result = LimitedProductsQuery.query(request)
        return Response(result.to_dict(), status=result.status_code)
    
    
class SmartSearchProductsView(APIView):
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]
    
    def get(self, request, query, *args, **kwargs):
        result = ProductListQuery.smart_search(query)
        return Response(result.to_dict(), status=result.status_code)


class AddRecentSearchView(APIView):
    """Add a new recent search"""
    permission_classes = [IsAuthenticated, IsCustomerPermission]

    def post(self, request):
        product_id = request.data.get("product_id")
        result = AddRecentSearchCommand.execute(request.user, product_id)
        return Response(result.to_dict(), status=result.status_code)


class RecentSearchListView(generics.ListAPIView):
    """Get all recent searches for the authenticated user"""
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        result = GetRecentSearchesQuery.query(request.user, request)
        return Response(result.data, status=result.status_code)


class DeleteRecentSearchView(APIView):
    """Delete a specific recent search by id"""
    permission_classes = [IsAuthenticated, IsCustomerPermission]

    def delete(self, request, search_id):
        result = DeleteRecentSearchCommand.execute(request.user, search_id)
        return Response(result.to_dict(), status=result.status_code)


class DeleteAllRecentSearchesView(APIView):
    """Delete all recent searches for the authenticated user"""
    permission_classes = [IsAuthenticated, IsCustomerPermission]

    def delete(self, request):
        result = DeleteAllRecentSearchesCommand.execute(request.user)
        return Response(result.to_dict(), status=result.status_code)

    
    
