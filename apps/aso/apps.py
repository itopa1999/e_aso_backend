from django.apps import AppConfig


class AsoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.aso'
    
    def ready(self):
        import apps.aso.signals
