from django.urls import path, include
from .views import *

urlpatterns = [
    path(
        "admin/",
        include(
            [
                path("dashboard/", DashboardAPIView.as_view()),
                path("products/", ProductAPIView.as_view()),
                path("orders/", OrderListView.as_view()),
                path('update-order/', UpdateOrderTrackingAPIView.as_view()),
                path('customers/', UserOrderListView.as_view()),
                path('bulk-update-badges/', BulkUpdateProductBadgesView.as_view())
                
            ]
        )
    ),
]