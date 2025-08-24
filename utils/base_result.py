from http import HTTPStatus

class BaseResult:
    def __init__(self, status_code=HTTPStatus.INTERNAL_SERVER_ERROR, message="An error occurred; please try again later"):
        self.status_code = status_code
        self.message = message

    @property
    def is_success(self):
        """Returns True if status_code is in 2xx range"""
        return str(self.status_code).startswith("2")

    def to_dict(self):
        return {
            "status_code": self.status_code,
            "message": self.message,
            "is_success": self.is_success,
        }


class BaseResultWithData(BaseResult):
    def __init__(self, data=None, status_code=HTTPStatus.INTERNAL_SERVER_ERROR, message="An error occurred; please try again later"):
        super().__init__(status_code, message)
        self.data = data

    def to_dict(self):
        base = super().to_dict()
        base["data"] = self.data
        return base



# USAGE

# return BaseResult(
#     status_code=HTTPStatus.BAD_REQUEST,
#     message="Invalid JSON data in request body"
# )


# return BaseResultWithData(
#     data=account_details,
#     status_code=HTTPStatus.OK,
#     message="Account verification successful"
# )
