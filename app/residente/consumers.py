from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json

class NoticiasConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("noticias", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("noticias", self.channel_name)

    async def enviar_noticias(self, event):
        noticias = event['noticias']
        await self.send(text_data=json.dumps({
            "noticias": noticias
        }))
