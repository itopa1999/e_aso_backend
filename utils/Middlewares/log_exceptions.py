import logging
import traceback

logger = logging.getLogger('django.request')

class ExceptionLoggingMiddleware:
    """
    Middleware to log full traceback for unhandled exceptions (500 errors).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Log the full traceback
            tb = traceback.format_exc()
            logger.error(f"Unhandled Exception at {request.path}:\n{tb}")
            raise
