from django.urls import path, include, re_path
from .views import *
from .analytics_views import *
urlpatterns = [
    path(
        "admin/",
        include(
            [
                path("send-token/", ResendOtpView.as_view()),
                path("telegram-login/", TelegramLoginVerificationView.as_view()),
                path("dashboard/", DashboardAPIView.as_view()),
                path("products/", ProductAPIView.as_view()),
                path("orders/", OrderListView.as_view()),
                # path('update-order/', UpdateOrderTrackingAPIView.as_view()),
                path('customers/', UserOrderListView.as_view()),
                path('bulk-update-badges/', BulkUpdateProductBadgesView.as_view()),
                path('import-products/', ProductBulkImportView.as_view(), name='import-products'),
                path('activate-products/', ActivateProductsAPIView.as_view()),
                re_path(r'^banners(?:/(?P<category>[\w,]+))?/?$', BannerListView.as_view()),
                path('feedbacks/', ListCustomerFeedbackView.as_view()),
                path('create/feedback/', CreateCustomerFeedbackView.as_view()),
                path('feedbacks/<int:pk>/mark_done/', MarkCustomerFeedbackDoneView.as_view()),
                path('def-testing/', DefTestingView.as_view()),
                path('transactions/', TransactionListView.as_view()),
                path("login/", LoginAPIView.as_view(), name="login"),
                path("change-password/", ResetPasswordAPIView.as_view()),
                path("feature-flags/", FeatureFlagListView.as_view()),
                path("contact-form-submissions/", ContactFormSubmissionListView.as_view()),
            ]
        )
    ),
    path(
        "analytics/",
        include(
            [
                path("revenue/", RevenueOverTimeAPIView.as_view()),
                path("orders/daily/", OrdersPerDayAPIView.as_view()),
                path("categories/sales/", CategorySalesAPIView.as_view()),
                path("products/top/", TopProductsAPIView.as_view()),

                # Customers
                path("customers/insights/", CustomerInsightsAPIView.as_view()),
                path("customers/top-buyers/", TopBuyersAPIView.as_view()),
                path("customers/locations/", CustomerLocationsAPIView.as_view()),
                path("customers/metrics/", CustomerMetricsAPIView.as_view()),

                # Products
                path("products/viewed/", MostViewedProductsAPIView.as_view()),
                path("products/rated/", TopRatedProductsAPIView.as_view()),

                # Fulfillment
                path("orders/fulfillment/", FulfillmentStatsAPIView.as_view()),
            ]
        )
    ),
]