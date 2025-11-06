import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import residente.routing as residente_routing
import usuario.routing as usuario_routing

from .routing import application



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            residente_routing.websocket_urlpatterns +
            usuario_routing.websocket_urlpatterns 
        )
    ),
})
