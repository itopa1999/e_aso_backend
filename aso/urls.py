from django.urls import path, include
from .views import *

urlpatterns = [
    path(
        "product/",
        include(
            [
                path("", ProductListView.as_view()),
                path('<int:id>/', ProductDetailView.as_view(), name='product-detail'),
                path("categories/", CategoriesView.as_view()),
                path("lists/", UserOrderListView.as_view()),
                path('order-details/<int:pk>/', OrderDetailView.as_view()),
                path('watchlist-and-cart-count/', CartAndWatchlistCountView.as_view()),
                path("cart/reorder/", ReorderItemsView.as_view()),
                path('watchlist-products/', WatchlistProductsView.as_view()),
                path("remove-all-watchlist/", RemoveAllWatchlistView.as_view()),
                path('toggle-watchlist/<int:product_id>/', ToggleWatchlistView.as_view()),
                path('move-all-to-cart/', MoveAllToCartView.as_view()),
                path('cart/', CartDetailAPIView.as_view(), name='cart-detail'),
                path('add-to-cart/', AddToCartView.as_view()),
                path('cart/update-quantity/', UpdateCartQuantityView.as_view()),
                path('cart/update-desc/', UpdateCartDescView.as_view()),
                path('cart/remove-item/', RemoveCartItemView.as_view()),
                path("cart/update-state/", UpdateCartStateView.as_view(), name="update-cart-state"),
                path('place-orders/', PlaceOrderView.as_view(), name='place-order'),
                path('paystack-confirm-subscription/<str:reference>/', PaystackConfirmSubscriptionView.as_view(), name='paystack-confirm-subscription'),
                path('import-products/', ProductBulkImportView.as_view(), name='import-products'),
                path('activate-products/', ActivateProductsAPIView.as_view()),
                path('delivery-fees/', DeliveryFeeAPIView.as_view(), name='delivery-fees'),
                
                path('rider/', RiderDashboardView.as_view()),
                path('orders/send-otp/', SendOtpView.as_view(), name='send-otp'),
                path('orders/verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
                path('orders/confirm/', MarkOrderAsDeliveredView.as_view()),
                path('orders/rider-details/', RiderOderDetailsView.as_view()),
                
                
                
            ]
        )
    ),
]