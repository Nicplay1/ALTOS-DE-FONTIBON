# administrador/signals.py
from django.db.models.signals import post_save, post_delete

from django.dispatch import receiver
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from usuario.models import *

@receiver(post_save, sender=Usuario)
def usuario_post_save(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()

    # Renderizamos la tabla completa (o solo la fila si prefieres)
    usuarios = Usuario.objects.select_related("id_rol").all()
    roles = Rol.objects.all()
    html = render_to_string("administrador/usuario/tabla_usuarios.html", {
        "usuarios": usuarios,
        "roles": roles
    })

    action = "refresh"  # puedes definir 'add' o 'update' si quieres otra lógica

    async_to_sync(channel_layer.group_send)(
        "usuarios_group",
        {
            "type": "usuarios_update",  # se mapea al método usuarios_update en consumer
            "action": action,
            "html": html,
            "created": created,
            "usuario_id": instance.id_usuario,
            "nombres": instance.nombres,
            "apellidos": instance.apellidos,
        }
    )

def enviar_reservas_update(action, instance):
    channel_layer = get_channel_layer()

    # Renderizar tabla completa
    reservas = Reserva.objects.select_related("cod_usuario", "cod_zona").all().order_by("-fecha_reserva")

    html = render_to_string("administrador/reservas/tabla_reservas.html", {
        "reservas": reservas
    })

    async_to_sync(channel_layer.group_send)(
        "reservas_group",
        {
            "type": "reservas_update",
            "action": action,
            "html": html,
            "reserva_id": instance.id_reserva
        }
    )

@receiver(post_save, sender=Reserva)
def reserva_creada_o_editada(sender, instance, created, **kwargs):
    if created:
        enviar_reservas_update("created", instance)
    else:
        enviar_reservas_update("updated", instance)

@receiver(post_delete, sender=Reserva)
def reserva_eliminada(sender, instance, **kwargs):
    enviar_reservas_update("deleted", instance)