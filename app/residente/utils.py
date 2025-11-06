# residente/utils.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.template.loader import render_to_string
from residente.models import Noticias

def enviar_noticias_ws():
    noticias_list = Noticias.objects.all().order_by('-fecha_publicacion')
    html = render_to_string('residente/detalles_residente/_noticias_list.html', {'noticias': noticias_list})

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "noticias",
        {
            "type": "enviar_noticias",
            "html": html
        }
    )
