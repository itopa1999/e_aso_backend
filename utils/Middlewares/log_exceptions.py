import logging

from backend import settings
from utils.base_result import BaseResult

logger = logging.getLogger(__name__)

class ExceptionLoggingMiddleware:
    """
    Middleware to log full traceback for unhandled exceptions (500 errors).
    """
    """
    Middleware that intercepts unhandled exceptions (HTTP 500)
    and returns a safe, generic JSON response for API requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Log the actual error for internal debugging
            logger.exception("Unhandled exception: %s", str(e))
            print("is_api_request:")
            # If it's an API path, return a generic JSON response
            is_api_request = (
                "/api/" in request.path.lower()
                or request.headers.get("Accept") == "application/json"
                or request.content_type == "application/json"
            )
            
            
            if is_api_request:
                return BaseResult({
                    "status_code": 500,
                    "message": "An unexpected error occurred on the server. Please try again later."
                }, status=500).to_response()

            # Otherwise, use Django's default error behavior (e.g., for HTML)
            if settings.DEBUG:
                raise e  # Let Django show detailed trace in debug mode
            return BaseResult({
                "status_code": 500,
                "message": "Something went wrong."
            }, status=500).to_response()
