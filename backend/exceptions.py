import drf_standardized_errors.handler
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException


@api_view()
def error_handler(request, exception=APIException()):
    return drf_standardized_errors.handler.exception_handler(
        exception, {"request": request}
    )
