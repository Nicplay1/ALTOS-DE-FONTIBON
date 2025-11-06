from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # URL para actualizaciones de usuarios (administrador)
    path("ws/usuarios/", consumers.UsuarioConsumer.as_asgi()),
]
