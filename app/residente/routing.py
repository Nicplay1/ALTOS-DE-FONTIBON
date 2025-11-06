from django.urls import re_path
from .consumers import NoticiasConsumer

websocket_urlpatterns = [
    re_path(r'ws/noticias/$', NoticiasConsumer.as_asgi()),
]
