from http import HTTPStatus
from apps.aso.models import LookUp
from utils.base_result import BaseResultWithData


class LookUpListQuery:
    @staticmethod
    def query():
        try:
            lookups = LookUp.objects.filter(is_deleted=False)
            return BaseResultWithData(
                data=lookups,
                status_code=HTTPStatus.OK,
                message="Lookups retrieved successfully."
            )
        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to fetch lookups: {str(e)}"
            )
