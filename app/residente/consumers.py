import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NoticiasConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Todos los usuarios se unen al grupo "noticias"
        await self.channel_layer.group_add("noticias", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("noticias", self.channel_name)

    # Recibir mensaje del grupo
    async def enviar_noticias(self, event):
        noticias = event['noticias']
        await self.send(text_data=json.dumps({
            "noticias": noticias
        }))
