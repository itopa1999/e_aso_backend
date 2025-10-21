# apps/aso/commands/remove_all_watchlist_command.py
from http import HTTPStatus
from apps.aso.models import WatchList
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger


class RemoveAllWatchlistCommand:
    @staticmethod
    def execute(user):
        op = OperationLogger("Remove all watchlist items", user=user.id if user else "Anonymous")
        op.start()
        
        try:
            deleted_count, _ = WatchList.objects.filter(
                user=user, is_deleted=False
            ).delete()
            
            op.success(f"Deleted {deleted_count} watchlist items")

            return BaseResultWithData(
                data={"deleted_count": deleted_count},
                status_code=HTTPStatus.OK,
                message=f"{deleted_count} watchlist items removed"
            )
        except Exception as e:
            op.fail(str(e))
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to remove watchlist items: {str(e)}"
            )
