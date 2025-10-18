from http import HTTPStatus
from apps.users.serializers import UserUpdateSerializer
from utils.base_result import BaseResult


class UpdateUserCommand:

    @staticmethod
    def Execute(user, update_data):
        try:
            serializer = UserUpdateSerializer(user, data=update_data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return BaseResult(
                    status_code=HTTPStatus.OK,
                    message="User updated successfully"
                )

            return BaseResult(
                status_code=HTTPStatus.BAD_REQUEST,
                message=serializer.errors
            )

        except Exception as e:
            return BaseResult(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"User update failed: {str(e)}"
            )