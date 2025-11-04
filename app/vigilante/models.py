from django.db import models

class Paquete(models.Model):
    id_paquete = models.AutoField(primary_key=True, db_column='id_paquete')
    apartamento = models.IntegerField()
    torre = models.IntegerField()
    fecha_recepcion = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=255, null=True, blank=True)

    # Usar string "usuario.Usuario" en vez de la clase directamente
    cod_usuario_recepcion = models.ForeignKey(
        'usuario.Usuario',
        related_name='paquetes_recepcion',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    cod_usuario_entrega = models.ForeignKey(
        'usuario.Usuario',
        related_name='paquetes_entrega',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    nombre_residente = models.CharField(max_length=100, null=True, blank=True)
    foto_cedula = models.ImageField(upload_to='cedulas_entrega/', null=True, blank=True)

    class Meta:
        db_table = 'paquete'
        managed = True

    def __str__(self):
        return f"Paquete {self.id_paquete} - Torre {self.torre}, Apto {self.apartamento}"
