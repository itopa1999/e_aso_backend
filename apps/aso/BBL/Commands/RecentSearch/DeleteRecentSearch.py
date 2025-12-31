from http import HTTPStatus
from apps.aso.models import RecentSearch
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger


class DeleteRecentSearchCommand:
    @staticmethod
    def execute(user, search_id):
        op = OperationLogger(
            "DeleteRecentSearchCommand",
            user=user.id if user else "Anonymous",
            search_id=search_id
        )
        op.start()
        
        try:
            recent_search = RecentSearch.objects.get(
                id=search_id,
                user=user,
                is_deleted=False
            )
            recent_search.is_deleted = True
            recent_search.save(update_fields=['is_deleted'])
            
            op.success("Recent search deleted successfully")
            return BaseResultWithData(
                data={"id": search_id},
                status_code=HTTPStatus.OK,
                message="Recent search deleted successfully"
            )
        except RecentSearch.DoesNotExist as e:
            op.fail("Recent search not found", e)
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.NOT_FOUND,
                message="Recent search not found"
            )
        except Exception as e:
            op.fail("Error deleting recent search", e)
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Error deleting recent search"
            )


class DeleteAllRecentSearchesCommand:
    @staticmethod
    def execute(user):
        op = OperationLogger(
            "DeleteAllRecentSearchesCommand",
            user=user.id if user else "Anonymous"
        )
        op.start()
        
        try:
            deleted_count = RecentSearch.objects.filter(
                user=user,
                is_deleted=False
            ).update(is_deleted=True)
            
            op.success(f"{deleted_count} recent searches deleted")
            return BaseResultWithData(
                data={"deleted_count": deleted_count},
                status_code=HTTPStatus.OK,
                message=f"{deleted_count} recent searches deleted successfully"
            )
        except Exception as e:
            op.fail("Error deleting recent searches", e)
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Error deleting recent searches"
            )
