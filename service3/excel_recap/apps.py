from django.apps import AppConfig

class ExcelRecapConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Add this line
    name = 'excel_recap'
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'excel_recap'

    def ready(self):

        from service3.eureka_client import start_eureka_client
        start_eureka_client()


