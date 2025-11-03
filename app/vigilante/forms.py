from django import forms
from usuario.models import Usuario
from .models import *
from datetime import date


class BuscarPlacaForm(forms.Form):
    placa = forms.CharField(
        max_length=10,
        label="Buscar Placa",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ejemplo: ABC123'
        })
    )


class VisitanteForm(forms.ModelForm):
    TIPO_VEHICULO_CHOICES = [
        ('Carro', 'Carro'),
        ('Moto', 'Moto'),
    ]

    tipo_vehiculo = forms.ChoiceField(
        choices=TIPO_VEHICULO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Visitante
        fields = [
            'nombres', 'apellidos', 'celular', 'documento',
            'tipo_vehiculo', 'placa', 'torre', 'apartamento'
        ]
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'placa': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'torre': forms.TextInput(attrs={'class': 'form-control'}),
            'apartamento': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DetalleParqueaderoForm(forms.ModelForm):
    class Meta:
        model = DetallesParqueadero
        fields = ['tipo_propietario', 'hora_salida', 'id_parqueadero']
        widgets = {
            'tipo_propietario': forms.Select(attrs={'class': 'form-control'}),
            'hora_salida': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'id_parqueadero': forms.Select(attrs={'class': 'form-control'}),
        }


class RegistroCorrespondenciaForm(forms.ModelForm):
    class Meta:
        model = RegistroCorrespondencia
        fields = ['tipo', 'descripcion', 'fecha_registro', 'cod_vigilante']
        widgets = {
            'fecha_registro': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].initial = 'Recibo'
        self.fields['tipo'].disabled = True
        self.fields['tipo'].widget.attrs.update({'class': 'form-control'})
        self.fields['fecha_registro'].initial = date.today()
        for field_name, field in self.fields.items():
            if field_name not in ['tipo', 'fecha_registro']:
                field.widget.attrs['class'] = 'form-control'
        self.fields['cod_vigilante'].queryset = Usuario.objects.filter(id_rol=4)


class BuscarResidenteForm(forms.Form):
    apartamento = forms.IntegerField(label="Apartamento", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    torre = forms.IntegerField(label="Torre", widget=forms.NumberInput(attrs={'class': 'form-control'}))


class RegistrarPaqueteForm(forms.ModelForm):
    class Meta:
        model = Paquete
        fields = ['apartamento', 'torre', 'descripcion', 'cod_usuario_recepcion']
        widgets = {
            'apartamento': forms.NumberInput(attrs={'class': 'form-control-modern'}),
            'torre': forms.NumberInput(attrs={'class': 'form-control-modern'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control-modern'}),
            'cod_usuario_recepcion': forms.Select(attrs={'class': 'form-control-modern'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cod_usuario_recepcion'].queryset = Usuario.objects.filter(id_rol=4)


class EntregaPaqueteForm(forms.ModelForm):
    class Meta:
        model = Paquete
        fields = ['id_paquete', 'nombre_residente', 'foto_cedula', 'cod_usuario_entrega']
        widgets = {
            'id_paquete': forms.HiddenInput(attrs={'id': 'entregaPaqueteId'}),
            'nombre_residente': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'foto_cedula': forms.ClearableFileInput(attrs={'class': 'form-control-modern'}),
            'cod_usuario_entrega': forms.Select(attrs={'class': 'form-control-modern'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cod_usuario_entrega'].queryset = Usuario.objects.filter(id_rol=4)


TIPO_CHOICES = (
    ('paquete', 'Daño de Paquete'),
    ('visitante', 'Daño de Vehículo'),
)

class NovedadesForm(forms.ModelForm):
    tipo_novedad = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    id_paquete = forms.ModelChoiceField(
        queryset=Paquete.objects.all(),
        required=False
    )
    id_visitante = forms.ModelChoiceField(
        queryset=Visitante.objects.all(),
        required=False
    )
    id_usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(id_rol=4),
        required=True
    )

    class Meta:
        model = Novedades
        fields = ['tipo_novedad', 'id_paquete', 'id_visitante', 'id_usuario', 'descripcion', 'foto']
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
