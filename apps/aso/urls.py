from django.urls import path, include
from .views import *

urlpatterns = [
    path(
        "product/",
        include(
            [
                path("", ProductListView.as_view()),
                path('<int:id>/', ProductDetailView.as_view(), name='product-detail'),
                path("lookups/", LookUpView.as_view()),
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
                path('monnify-confirm/<str:reference>/', MonnifyConfirmView.as_view(), name='monnify-confirm'),
                path('flutterwave-confirm/<str:reference>/', FlutterwaveConfirmView.as_view(), name='flutterwave-confirm'),
                path('delivery-fees/', DeliveryFeeAPIView.as_view(), name='delivery-fees'),
                path("cart/clear/", ClearCartView.as_view()),
                path("track-order/<int:order_id>/", TrackingDetailsView.as_view()),
                path("feature-flag/<str:feature_name>/", CheckFeatureFlagView.as_view()),
                path("limited-products/", LimitedProductsView.as_view()),
                path(
                    "smart-search/<str:query>/",
                    SmartSearchProductsView.as_view()
                ),
                path("recent-searches/", RecentSearchListView.as_view(), name='recent-searches-list'),
                path("recent-searches/add/", AddRecentSearchView.as_view(), name='add-recent-search'),
                path("recent-searches/<int:search_id>/", DeleteRecentSearchView.as_view(), name='delete-recent-search'),
                path("recent-searches/delete-all/", DeleteAllRecentSearchesView.as_view(), name='delete-all-recent-searches'),
                path("highest-price/", HighestPriceProductsView.as_view(), name='highest-price-products'),
                path("recover-order/<int:order_id>/", RecoverFailedOrderView.as_view(), name='recover-failed-order'),
            ]
        )
    ),                
]
