# apps/aso/commands/toggle_watchlist_command.py
from http import HTTPStatus
from apps.aso.models import WatchList
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger


class ToggleWatchlistCommand:
    @staticmethod
    def execute(user, product_id):
        op = OperationLogger("Toggle watchlist item", user=user.id if user else "Anonymous", product_id=product_id)
        op.start()
        try:
            watchlist_item, created = WatchList.objects.get_or_create(
                user=user,
                product_id=product_id,
                is_deleted=False
            )

            if not created:
                watchlist_item.delete()
                op.success(f"Removed product {product_id} from watchlist")
                return BaseResultWithData(
                    data={"watchlisted": False},
                    status_code=HTTPStatus.OK,
                    message="Product removed from watchlist"
                )
                
            op.success(f"Added product {product_id} to watchlist")
            return BaseResultWithData(
                data={"watchlisted": True},
                status_code=HTTPStatus.OK,
                message="Product added to watchlist"
            )

        except Exception as e:
            op.fail(str(e))
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to toggle watchlist: {str(e)}"
            )
