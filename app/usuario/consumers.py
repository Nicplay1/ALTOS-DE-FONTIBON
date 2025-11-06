import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
from .models import *

class UsuarioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("usuarios_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("usuarios_group", self.channel_name)

    async def usuario_actualizado(self, event):
        html = render_to_string("administrador/usuario/tabla_usuarios.html", {
            "usuarios": Usuario.objects.select_related("id_rol").all(),
            "roles": Rol.objects.all(),
        })
        await self.send(text_data=json.dumps({"html": html}))
