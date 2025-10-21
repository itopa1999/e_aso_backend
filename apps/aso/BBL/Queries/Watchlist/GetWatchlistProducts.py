# apps/aso/queries/get_watchlist_products_query.py
from http import HTTPStatus
from apps.aso.models import Product
from apps.aso.serializers import WatchlistProductSerializer
from utils.base_result import BaseResultWithData


class GetWatchlistProductsQuery:
    @staticmethod
    def query(user, request=None):
        try:
            queryset = Product.objects.filter(
                watchlist_product__user=user,
                is_deleted=False
            )

            serializer = WatchlistProductSerializer(queryset, many=True, context={"request": request})
            return BaseResultWithData(
                data=serializer.data,
                status_code=HTTPStatus.OK,
                message="Watchlist fetched successfully"
            )
        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to get watchlist: {str(e)}"
            )
