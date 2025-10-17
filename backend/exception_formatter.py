from drf_standardized_errors.formatter import (
    ExceptionFormatter as BaseExceptionFormatter,
)
from drf_standardized_errors.types import ErrorResponse


import uuid
from http import HTTPStatus
from utils.base_result import BaseResult 

class ExceptionFormatter(BaseExceptionFormatter):
    def format_error_response(self, error_response: ErrorResponse):
        error = error_response.errors[0]

        return BaseResult(
            status_code=HTTPStatus.BAD_REQUEST,
            message=f"{error.attr}: {error.detail}",
            request_id=str(uuid.uuid4())
        ).to_dict()