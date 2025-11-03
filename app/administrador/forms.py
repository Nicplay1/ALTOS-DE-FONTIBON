from django import forms
from usuario.models import *
from django.utils import timezone

# ---------------- CAMBIAR ROL ----------------
class CambiarRolForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['id_rol']
        labels = {'id_rol': 'Rol'}
        widgets = {
            'id_rol': forms.Select(attrs={'class': 'form-select'})
        }


# ---------------- EDITAR RESERVA ----------------
class EditarReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ["observacion", "estado"]
        labels = {
            "observacion": "Observación",
            "estado": "Estado"
        }
        widgets = {
            "observacion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Escribe una observación..."
            }),
            "estado": forms.Select(attrs={"class": "form-select-modern"})
        }


# ---------------- NOTICIAS ----------------
class NoticiasForm(forms.ModelForm):
    class Meta:
        model = Noticias
        fields = ['titulo', 'descripcion']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el título'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese la descripción'
            }),
        }


# ---------------- VEHÍCULO RESIDENTE (documentos) ----------------
class VehiculoResidenteForm(forms.ModelForm):
    class Meta:
        model = VehiculoResidente
        fields = ['documentos']
        widgets = {
            'documentos': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['documentos'].help_text = "Estado manual de validación. Sobrescribe la validación automática."


# ---------------- SORTEO ----------------
class SorteoForm(forms.ModelForm):
    tipo_residente_propietario = forms.BooleanField(
        required=False,
        label='Propietario',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Sorteo
        fields = ['tipo_residente_propietario', 'fecha_inicio', 'hora_sorteo']
        labels = {
            'fecha_inicio': 'Fecha de Inicio',
            'hora_sorteo': 'Hora del Sorteo',
        }
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_sorteo': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def clean_fecha_inicio(self):
        fecha = self.cleaned_data.get('fecha_inicio')
        if fecha and fecha < timezone.now().date():
            raise forms.ValidationError("No puedes seleccionar una fecha pasada.")
        return fecha


# ---------------- ESTADO PAGO ----------------
class EstadoPagoForm(forms.ModelForm):
    class Meta:
        model = PagosReserva
        fields = ["estado"]
        widgets = {
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
