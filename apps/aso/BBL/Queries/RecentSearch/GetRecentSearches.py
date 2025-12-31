from http import HTTPStatus
from apps.aso.models import RecentSearch
from apps.aso.serializers import SimpleRecentSearchSerializer
from utils.base_result import BaseResultWithData


class GetRecentSearchesQuery:
    @staticmethod
    def query(user, request=None):
        try:
            if not user.is_authenticated:
                return BaseResultWithData(
                    data=[],
                    status_code=HTTPStatus.OK,
                    message="Recent searches retrieved"
                )
            
            recent_searches = RecentSearch.objects.filter(
                user=user,
                is_deleted=False
            ).order_by('-created_at')
            
            serializer = SimpleRecentSearchSerializer(
                recent_searches, 
                many=True,
                context={'request': request}
            )
            return BaseResultWithData(
                data=serializer.data,
                status_code=HTTPStatus.OK,
                message="Recent searches retrieved successfully"
            )
        except Exception as e:
            return BaseResultWithData(
                data=[],
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Error retrieving recent searches"
            )
