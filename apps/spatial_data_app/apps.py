from django.apps import AppConfig

class SpatialDataAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.spatial_data_app'   # <-- IMPORTANT: full dotted path

