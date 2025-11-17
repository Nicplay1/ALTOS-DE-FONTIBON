from django import forms
from .models import Usuario
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import re


class RegisterForm(forms.Form):
    nombres = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellidos = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipo_documento = forms.ChoiceField(
        choices=[('CC', 'CC'), ('CE', 'CE'), ('TI', 'TI'), ('Pasaporte', 'Pasaporte')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    numero_documento = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    correo = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    celular = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    contraseña = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirmar_contraseña = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class LoginForm(forms.Form):
    numero_documento = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Documento de Identidad"
    )
    contraseña = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña"
    )


class UsuarioUpdateForm(forms.ModelForm):
    contraseña = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['correo', 'celular', 'telefono', 'contraseña']
        widgets = {
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Usuario.objects.exclude(pk=self.instance.pk).filter(correo=correo).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return correo

    def save(self, commit=True):
        usuario = super().save(commit=False)
        nueva_contrasena = self.cleaned_data.get('contraseña')

        if nueva_contrasena:  # solo actualiza si se ingresa algo
            usuario.contraseña = make_password(nueva_contrasena)
        else:
            # si no hay contraseña nueva, mantenemos la que ya estaba
            usuario.contraseña = Usuario.objects.get(pk=usuario.pk).contraseña

        if commit:
            usuario.save()
        return usuario
