from django.urls import path,re_path
from .consumers import *

websocket_urlpatterns = [
    # ruta para el panel administrador
    path("ws/usuarios/", AdminUserConsumer.as_asgi()),
    path("ws/reservas/", ReservasConsumer.as_asgi()),
    
]
