# vigilante/management/commands/enviar_recordatorio_vencimiento.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from usuario.models import *

class Command(BaseCommand):
    help = "Envía recordatorio 1 día antes de que un documento de vehículo caduque."

    def handle(self, *args, **kwargs):
        hoy = timezone.now().date()
        fecha_recordatorio = hoy + timedelta(days=1)

        archivos_proximos_vencer = ArchivoVehiculo.objects.filter(
            fecha_vencimiento=fecha_recordatorio
        )

        if not archivos_proximos_vencer.exists():
            self.stdout.write("No hay archivos próximos a vencer.")
            return

        for archivo in archivos_proximos_vencer:
            vehiculo = archivo.id_vehiculo
            usuario = vehiculo.cod_usuario
            tipo_documento = archivo.id_tipo_archivo.tipo_documento
            fecha_vencimiento = archivo.fecha_vencimiento

            try:
                send_mail(
                    subject=f"Recordatorio: {tipo_documento} por vencer",
                    message=(
                        f"Hola {usuario.nombres} {usuario.apellidos},\n\n"
                        f"Este es un recordatorio de que el documento '{tipo_documento}' de tu vehículo {vehiculo.placa} "
                        f"vence el {fecha_vencimiento}.\n"
                        "Por favor, actualízalo antes de la fecha de vencimiento.\n\n"
                        "Atentamente,\nAdministración Altos de Fontibón"
                    ),
                    from_email="altosdefontibon.cr@gmail.com",
                    recipient_list=[usuario.correo],
                    fail_silently=False,
                )
                self.stdout.write(f"Correo enviado a {usuario.correo} por {tipo_documento}.")
            except Exception as e:
                self.stderr.write(f"Error al enviar correo a {usuario.correo}: {e}")
