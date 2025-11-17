from django.apps import AppConfig

class AdministradorConfig(AppConfig):
    name = "administrador"

    def ready(self):
        import administrador.signals

