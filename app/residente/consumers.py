# residente/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NoticiasConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("noticias", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("noticias", self.channel_name)

    # Recibir mensaje de servidor
    async def enviar_noticias(self, event):
        noticias_html = event['html']
        await self.send(text_data=json.dumps({
            'html': noticias_html
        }))
