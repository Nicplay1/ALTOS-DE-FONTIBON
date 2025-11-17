from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/usuarios/$", consumers.UsuariosConsumer.as_asgi()),
    re_path(r"ws/reservas/$", consumers.ReservasConsumer.as_asgi()),  # NUEVO
]
