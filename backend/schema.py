from drf_yasg.generators import OpenAPISchemaGenerator
from django.http import HttpResponse
from functools import wraps

class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema



def swagger_protect(view_func):
    """
    Decorator to protect Swagger/API documentation endpoints.
    
    Uses Django's is_staff permission check instead of basic auth credentials.
    This is more secure than basic auth with hardcoded credentials because:
    - Uses existing user authentication system
    - No credentials in environment variables
    - Can be revoked per user without code changes
    - Integrates with Django admin permissions
    
    Args:
        view_func: The view function to protect
        
    Returns:
        Wrapped view function with staff-only access
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return unauthorized_response()
        
        if not request.user.is_staff:
            return unauthorized_response()
        
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def unauthorized_response():
    
    response = HttpResponse(
        "<h2>Unauthorized</h2><p>Please provide valid Swagger credentials.</p>",
        status=401,
        content_type="text/html"
    )
    response['WWW-Authenticate'] = 'Basic realm="Swagger Docs"'
    return response
