# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.layers import get_channel_layer
from usuario.routing import websocket_urlpatterns as usuario_ws
# si tienes más apps, las importas igual: from otra_app.routing import websocket_urlpatterns as otra_app_ws

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            usuario_ws  # puedes concatenar más: usuario_ws + otra_app_ws + ...
        )
    ),
})
