from django.urls import path, include
from .views import *

urlpatterns = [
    path(
        "product/",
        include(
            [
                path("", ProductListView.as_view()),
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
                path('cart/remove-item/', RemoveCartItemView.as_view()),
                path('import-products/', ProductBulkImportView.as_view(), name='import-products'),
                
                
                
            ]
        )
    ),
]