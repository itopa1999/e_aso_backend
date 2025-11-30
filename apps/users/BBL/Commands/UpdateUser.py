from http import HTTPStatus
from apps.users.serializers import UserUpdateSerializer
from utils.base_result import BaseResult
from utils.log_helpers import OperationLogger


class UpdateUserCommand:

    @staticmethod
    def Execute(user, update_data):
        op = OperationLogger(
            "UpdateUserCommand",
            user=user.id if user else "Anonymous"
        )
        op.start()
        
        serializer = UserUpdateSerializer(user, data=update_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            op.success(f"User {user.id} updated successfully")
            return BaseResult(
                status_code=HTTPStatus.OK,
                message="User updated successfully"
            )

        op.fail(f"User update validation failed: {serializer.errors}")
        return BaseResult(
            status_code=HTTPStatus.BAD_REQUEST,
            message=serializer.errors
        )
