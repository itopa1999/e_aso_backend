from apps.aso.models import Product, FeatureFlag
from utils.base_result import BaseResultWithData
from utils.enum import FeatureNames
from utils.feature_flags import is_feature_enabled
from apps.aso.serializers import WatchlistProductSerializer
from rest_framework import serializers


class LimitedFlagSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(allow_null=True)
    end_date = serializers.DateTimeField(allow_null=True)
    discount_percent = serializers.FloatField(allow_null=True)
    is_enabled = serializers.BooleanField()


class LimitedProductsResponseSerializer(serializers.Serializer):
    limited_products = WatchlistProductSerializer(many=True, read_only=True)
    limited_flag = LimitedFlagSerializer(allow_null=True, read_only=True)


class LimitedProductsQuery:
    @staticmethod
    def query(request):
        limited_products = Product.objects.filter(
            is_limited=True, is_deleted=False, display_product=True
        )

        flag, enabled = is_feature_enabled(FeatureNames.PRODUCT_LIMITATION.value)

        if not flag:
            flag_obj = None
        else:
            # Pass the actual flag instance for nested serializer
            flag_obj = flag

        # Serialize the response properly
        response_serializer = LimitedProductsResponseSerializer(
            instance={
                "limited_products": limited_products,
                "limited_flag": flag_obj,
            },
            context={"request": request}
        )

        return BaseResultWithData(
            data=response_serializer.data,
            message="Limited products fetched successfully.",
            status_code=200,
        )