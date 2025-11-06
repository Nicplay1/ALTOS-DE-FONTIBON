from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import usuario.routing
 # si ya lo tienes

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            usuario.routing.websocket_urlpatterns 
             # otros canales
        )
    ),
})
