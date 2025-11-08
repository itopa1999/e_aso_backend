
from django.db.models import Q
from apps.administrator.serializers import FeatureFlagSerializer
from apps.aso.models import FeatureFlag
from utils.base_result import BaseResultWithData


class FeatureFlagListQuery:
    @staticmethod
    def query(search_params=None):
        
        featureFlag = FeatureFlag.objects.all()
        
        if search_params:
            featureFlag = featureFlag.filter(
                Q(name__icontains=search_params) |
                Q(description__icontains=search_params)           
            )
        serialized_data = FeatureFlagSerializer(featureFlag, many=True)
        return BaseResultWithData(
            data=serialized_data.data,
            message="Feature flags retrieved successfully",
            status_code=200
        )
        