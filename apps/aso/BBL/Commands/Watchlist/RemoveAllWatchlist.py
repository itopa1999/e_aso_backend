# apps/aso/commands/remove_all_watchlist_command.py
from http import HTTPStatus
from django.db import transaction
from apps.aso.models import WatchList
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger


class RemoveAllWatchlistCommand:
    @staticmethod
    def execute(user):
        op = OperationLogger("Remove all watchlist items", user=user.id if user else "Anonymous")
        op.start()
        
        with transaction.atomic():
            deleted_count, _ = WatchList.objects.filter(
                user=user, is_deleted=False
            ).delete()
        
        op.success(f"Deleted {deleted_count} watchlist items")

        return BaseResultWithData(
            data={"deleted_count": deleted_count},
            status_code=HTTPStatus.OK,
            message=f"{deleted_count} watchlist items removed"
        )

