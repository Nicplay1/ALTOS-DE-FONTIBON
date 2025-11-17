
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import administrador.routing  # donde pondremos las rutas ws

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_proyecto.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(administrador.routing.websocket_urlpatterns),
})
