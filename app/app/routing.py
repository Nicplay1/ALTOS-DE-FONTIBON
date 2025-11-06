from django.urls import path
from .consumers import AdminUserConsumer

websocket_urlpatterns = [
    # ruta para el panel administrador
    path("ws/usuarios/", AdminUserConsumer.as_asgi()),
]
