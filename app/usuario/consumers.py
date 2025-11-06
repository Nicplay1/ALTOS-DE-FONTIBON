# usuarios/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
from usuario.models import Usuario, Rol

class UsuariosConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("usuarios_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("usuarios_group", self.channel_name)

    async def receive(self, text_data):
        pass  # No recibimos datos del cliente

    async def enviar_lista_usuarios(self, event):
        usuarios = Usuario.objects.select_related("id_rol").all()
        html = render_to_string("administrador/usuario/tabla_usuarios.html", {
            "usuarios": usuarios,
            "roles": Rol.objects.all()
        })
        await self.send(text_data=json.dumps({
            "html": html
        }))
