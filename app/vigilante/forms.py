from django import forms
from usuario.models import *
from .models import *
from datetime import date


class BuscarPlacaForm(forms.Form):
    placa = forms.CharField(
        max_length=7,
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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- TORRES ---
        torres = [(i, f"Torre {i}") for i in range(1, 6)]

        # --- APARTAMENTOS ---
        apartamentos = []
        for piso in range(1, 17):
            for num in range(1, 10):
                apto = piso * 100 + num
                apartamentos.append((apto, f"Apartamento {apto}"))

        self.fields['torre'] = forms.ChoiceField(
            choices=torres,
            widget=forms.Select(attrs={'class': 'form-control'}),
            label="Torre"
        )
        self.fields['apartamento'] = forms.ChoiceField(
            choices=apartamentos,
            widget=forms.Select(attrs={'class': 'form-control'}),
            label="Apartamento"
        )

    # ---------------------------
    # VALIDACIONES PERSONALIZADAS
    # ---------------------------

    def clean_nombres(self):
        nombres = self.cleaned_data.get("nombres")

        if not nombres.replace(" ", "").isalpha():
            raise forms.ValidationError("El nombre solo puede contener letras y espacios.")

        return nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get("apellidos")

        if not apellidos.replace(" ", "").isalpha():
            raise forms.ValidationError("El apellido solo puede contener letras y espacios.")

        return apellidos

    def clean_documento(self):
        documento = self.cleaned_data.get("documento")

        if not documento.isdigit():
            raise forms.ValidationError("El documento solo puede contener números.")

        return documento

    def clean_celular(self):
        celular = self.cleaned_data.get("celular")

        if not celular.isdigit():
            raise forms.ValidationError("El celular solo puede contener números.")

        return celular


class DetallesParqueaderoForm(forms.ModelForm):
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
        fields = ['tipo', 'descripcion', 'cod_vigilante']  # ⚠ fecha_registro removido
        widgets = {
            'tipo': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'cod_vigilante': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].initial = 'Recibo'
        self.fields['tipo'].disabled = True
        self.fields['cod_vigilante'].queryset = Usuario.objects.filter(id_rol=4)


class BuscarResidenteForm(forms.Form):
    apartamento = forms.IntegerField(label="Apartamento", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    torre = forms.IntegerField(label="Torre", widget=forms.NumberInput(attrs={'class': 'form-control'}))


class RegistrarPaqueteForm(forms.Form):

    descripcion = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control-modern'}),
        label="Descripción del Paquete"
    )

    cod_usuario_recepcion = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(id_rol=4),
        empty_label="Seleccione vigilante",
        widget=forms.Select(attrs={'class': 'form-control-modern'}),
        label="Vigilante de Recepción"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # -------------------------
        # LISTA DE TORRES (1 a 5)
        # -------------------------
        torres = [(i, f"Torre {i}") for i in range(1, 6)]

        # -----------------------------------------------
        # LISTA DE APARTAMENTOS (piso 1–16, apto 101–1609)
        # -----------------------------------------------
        apartamentos = []
        for piso in range(1, 17):      # pisos 1 al 16
            for num in range(1, 10):   # aptos 1 al 9
                apto = piso * 100 + num
                apartamentos.append((apto, f"Apartamento {apto}"))

        # Campos reemplazados dinámicamente
        self.fields['torre'] = forms.ChoiceField(
            choices=torres,
            widget=forms.Select(attrs={'class': 'form-control-modern'}),
            label="Torre"
        )

        self.fields['apartamento'] = forms.ChoiceField(
            choices=apartamentos,
            widget=forms.Select(attrs={'class': 'form-control-modern'}),
            label="Apartamento"
        )

class EntregaPaqueteForm(forms.Form):
    id_paquete = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'id': 'entregaPaqueteId'})
    )

    nombre_residente = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control-modern'}),
        label="Recibido por"
    )

    foto_cedula = forms.ImageField(
        required=False, 
        label="Foto de Cédula del Residente",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-modern'})
    )

    cod_usuario_entrega = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(id_rol=4),
        empty_label="Seleccione vigilante",
        widget=forms.Select(attrs={'class': 'form-control-modern'}),
        label="Vigilante que Entrega"
    )


TIPO_CHOICES = (
    ('paquete', 'Daño de Paquete'),
    ('visitante', 'Daño de Vehículo'),
)

class NovedadesForm(forms.ModelForm):

    tipo_novedad = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Tipo de novedad"
    )

    id_paquete = forms.ModelChoiceField(
        queryset=Paquete.objects.all(),
        required=True,
        label="Paquete"
    )

    id_visitante = forms.ModelChoiceField(
        queryset=Visitante.objects.all(),
        required=True,
        label="Visitante"
    )

    id_usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(id_rol=4),
        required=True,
        label="Registrado por"
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

        # Forzar que todos los campos sean obligatorios
        for field in self.fields.values():
            field.required = True