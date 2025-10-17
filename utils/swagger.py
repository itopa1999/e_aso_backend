from drf_yasg.inspectors import SwaggerAutoSchema

class TaggedAutoSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys=None):
        # Check for custom tag set at the view class level
        manual_tag = getattr(self.view.__class__, 'swagger_tags', None)
        if manual_tag:
            return manual_tag if isinstance(manual_tag, list) else [manual_tag]
        
        # Fallback to app name
        app_label = self.view.__module__.split('.')[0]
        return [app_label.capitalize()]
