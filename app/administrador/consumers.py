# administrador/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class UsuariosConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "usuarios_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Recibir mensajes desde el grupo y enviarlos al cliente
    async def usuarios_update(self, event):
        # event contendrá keys: action (ej: "refresh"), html (tabla completa)
        await self.send(json.dumps(event))
        
        
class ReservasConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "reservas_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Evento enviado por signals
    async def reservas_update(self, event):
        await self.send(json.dumps(event))
