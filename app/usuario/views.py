from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import *
from .forms import *
from residente.forms import *
from .decorators import login_requerido
from django.core.mail import send_mail
from django.urls import reverse
import re
from django.contrib.auth import logout
import datetime
from django.http import JsonResponse
import json

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.template.loader import render_to_string

def register_view(request):

    if request.method == "POST":
        form = RegisterForm(request.POST)

        # Si es AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

            if not form.is_valid():
                field_errors = {field: errors[0] for field, errors in form.errors.items()}
                return JsonResponse({
                    "success": False,
                    "messages": ["Por favor, corrige los errores."],
                    "field_errors": field_errors
                })

            # Extraer datos
            data = form.cleaned_data
            nombres = data["nombres"]
            apellidos = data["apellidos"]
            tipo_documento = data["tipo_documento"]
            numero_documento = data["numero_documento"]
            correo = data["correo"]
            telefono = data["telefono"]
            celular = data["celular"]
            contraseña = data["contraseña"]
            confirmar_contraseña = data["confirmar_contraseña"]

            errors = {}

            # VALIDACIÓN: nombre/apellido
            if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$', nombres):
                errors["nombres"] = "El nombre no debe tener números ni caracteres especiales."

            if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$', apellidos):
                errors["apellidos"] = "El apellido no debe tener números ni caracteres especiales."

            # VALIDACIÓN: documento único
            if Usuario.objects.filter(numero_documento=numero_documento).exists():
                errors["numero_documento"] = "Este número de documento ya está registrado."

            # VALIDACIÓN: correo único
            if Usuario.objects.filter(correo=correo).exists():
                errors["correo"] = "Este correo ya está registrado."

            # VALIDACIÓN: celular
            if not re.fullmatch(r'\d{10}', celular):
                errors["celular"] = "El número de celular debe tener 10 dígitos."

            # VALIDACIÓN: teléfono
            if not re.fullmatch(r'\d{7}', telefono):
                errors["telefono"] = "El número de teléfono debe tener 7 dígitos."

            # VALIDACIÓN: contraseña fuerte
            if len(contraseña) < 12:
                errors["contraseña"] = "La contraseña debe tener mínimo 12 caracteres."

            if not re.search(r"[A-Z]", contraseña):
                errors["contraseña"] = "Debe tener al menos una letra mayúscula."

            if not re.search(r"\d", contraseña):
                errors["contraseña"] = "Debe tener al menos un número."

            if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=]", contraseña):
                errors["contraseña"] = "Debe tener un carácter especial."

            # VALIDACIÓN: confirmar contraseña
            if contraseña != confirmar_contraseña:
                errors["confirmar_contraseña"] = "Las contraseñas no coinciden."

            # SI HAY ERRORES
            if errors:
                return JsonResponse({
                    "success": False,
                    "messages": ["Hay errores en el formulario."],
                    "field_errors": errors
                })

            # CREACIÓN DEL USUARIO
            usuario = Usuario(
                nombres=nombres,
                apellidos=apellidos,
                tipo_documento=tipo_documento,
                numero_documento=numero_documento,
                correo=correo,
                telefono=telefono,
                celular=celular,
                contraseña=make_password(contraseña),
                id_rol_id=1
            )
            usuario.save()

            return JsonResponse({
                "success": True,
                "messages": ["Usuario registrado correctamente."],
                "redirect_url": "/login/"
            })

        # NO AJAX
        else:
            if form.is_valid():
                data = form.cleaned_data

                # mismas validaciones arriba…
                # (si quieres te la hago también completa en el flujo normal)

                usuario = Usuario(
                    nombres=data["nombres"],
                    apellidos=data["apellidos"],
                    tipo_documento=data["tipo_documento"],
                    numero_documento=data["numero_documento"],
                    correo=data["correo"],
                    telefono=data["telefono"],
                    celular=data["celular"],
                    contraseña=make_password(data["contraseña"])
                )
                usuario.save()

                messages.success(request, "Usuario registrado correctamente.")
                return redirect("login")

    else:
        form = RegisterForm()

    return render(request, "usuario/register.html", {"form": form})



def login_view(request):
    if "intentos_fallidos" not in request.session:
        request.session["intentos_fallidos"] = 0
    if "bloqueado_hasta" not in request.session:
        request.session["bloqueado_hasta"] = None

    # Verificar si está bloqueado
    if request.session["bloqueado_hasta"]:
        bloqueado_hasta = datetime.datetime.fromisoformat(request.session["bloqueado_hasta"])
        if datetime.datetime.now() < bloqueado_hasta:
            minutos_restantes = (bloqueado_hasta - datetime.datetime.now()).seconds // 60
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'messages': [f"Has superado los intentos. Intenta de nuevo en {minutos_restantes} minutos."]
                })
            else:
                messages.error(request, f"Has superado los intentos. Intenta de nuevo en {minutos_restantes} minutos.")
                return render(request, "usuario/inicio_sesion.html", {"form": LoginForm()})
        else:
            # Resetear bloqueo cuando ya pasó el tiempo
            request.session["intentos_fallidos"] = 0
            request.session["bloqueado_hasta"] = None

    if request.method == "POST":
        form = LoginForm(request.POST)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Procesar AJAX
            if form.is_valid():
                numero_documento = form.cleaned_data['numero_documento']
                contraseña = form.cleaned_data['contraseña']

                try:
                    usuario = Usuario.objects.get(numero_documento=numero_documento)
                    if check_password(contraseña, usuario.contraseña):
                        # Reiniciar intentos
                        request.session["intentos_fallidos"] = 0
                        request.session["bloqueado_hasta"] = None

                        # Guardar sesión
                        request.session['usuario_id'] = usuario.id_usuario
                        request.session['rol_id'] = usuario.id_rol_id

                        # Determinar URL de redirección
                        if usuario.id_rol_id == 1:
                            redirect_url = "/"
                        elif usuario.id_rol_id == 2:
                            redirect_url = "/residente/residente/"
                        elif usuario.id_rol_id == 3:
                            redirect_url = "/administrador/panel/"
                        elif usuario.id_rol_id == 4:
                            redirect_url = "/vigilante/panel/"
                        else:
                            redirect_url = "index"

                        return JsonResponse({
                            'success': True,
                            'redirect_url': redirect_url,
                            'welcome_message': f"¡Bienvenido {usuario.nombres} {usuario.apellidos}!"
                        })
                    else:
                        request.session["intentos_fallidos"] += 1
                        if request.session["intentos_fallidos"] >= 5:
                            # Bloquear por 15 minutos
                            bloqueado_hasta = datetime.datetime.now() + datetime.timedelta(minutes=15)
                            request.session["bloqueado_hasta"] = bloqueado_hasta.isoformat()
                            return JsonResponse({
                                'success': False,
                                'messages': ["Has superado los intentos. Intenta de nuevo en 15 minutos."],
                                'field_errors': {
                                    'contraseña': "Contraseña incorrecta"
                                }
                            })
                        else:
                            restantes = 5 - request.session["intentos_fallidos"]
                            return JsonResponse({
                                'success': False,
                                'messages': [f"Contraseña incorrecta. Intentos restantes: {restantes}"],
                                'field_errors': {
                                    'contraseña': "Contraseña incorrecta"
                                }
                            })
                except Usuario.DoesNotExist:
                    request.session["intentos_fallidos"] += 1
                    if request.session["intentos_fallidos"] >= 5:
                        bloqueado_hasta = datetime.datetime.now() + datetime.timedelta(minutes=15)
                        request.session["bloqueado_hasta"] = bloqueado_hasta.isoformat()
                        return JsonResponse({
                            'success': False,
                            'messages': ["Has superado los intentos. Intenta de nuevo en 15 minutos."],
                            'field_errors': {
                                'documento': "Documento no registrado"
                            }
                        })
                    else:
                        restantes = 5 - request.session["intentos_fallidos"]
                        return JsonResponse({
                            'success': False,
                            'messages': [f"Documento no registrado. Intentos restantes: {restantes}"],
                            'field_errors': {
                                'documento': "Documento no registrado"
                            }
                        })
            else:
                # Form no válido
                field_errors = {}
                for field, errors in form.errors.items():
                    field_name = 'documento' if field == 'numero_documento' else 'password'
                    field_errors[field_name] = errors[0]
                
                return JsonResponse({
                    'success': False,
                    'messages': ['Por favor, corrige los errores en el formulario.'],
                    'field_errors': field_errors
                })
        
        else:
            # Procesamiento normal (no AJAX)
            if form.is_valid():
                numero_documento = form.cleaned_data['numero_documento']
                contraseña = form.cleaned_data['contraseña']

                try:
                    usuario = Usuario.objects.get(numero_documento=numero_documento)
                    if check_password(contraseña, usuario.contraseña):
                        # Reiniciar intentos
                        request.session["intentos_fallidos"] = 0
                        request.session["bloqueado_hasta"] = None

                        # Guardar sesión
                        request.session['usuario_id'] = usuario.id_usuario
                        request.session['rol_id'] = usuario.id_rol_id
                        messages.success(request, f"Bienvenido {usuario.nombres} {usuario.apellidos}!")

                        # Redirigir por rol
                        if usuario.id_rol_id == 1:
                            return redirect("index")
                        elif usuario.id_rol_id == 2:
                            return redirect("detalle_residente")
                        elif usuario.id_rol_id == 3:
                            return redirect("panel_administrador")
                        elif usuario.id_rol_id == 4:
                            return redirect("panel_vigilante")
                        elif usuario.id_rol_id == 5:
                            return redirect("asistente_home")
                    else:
                        request.session["intentos_fallidos"] += 1
                        if request.session["intentos_fallidos"] >= 5:
                            # Bloquear por 15 minutos
                            bloqueado_hasta = datetime.datetime.now() + datetime.timedelta(minutes=15)
                            request.session["bloqueado_hasta"] = bloqueado_hasta.isoformat()
                            messages.error(request, "Has superado los intentos. Intenta de nuevo en 15 minutos.")
                        else:
                            restantes = 5 - request.session["intentos_fallidos"]
                            messages.error(request, f"Contraseña incorrecta. Intentos restantes: {restantes}")
                except Usuario.DoesNotExist:
                    request.session["intentos_fallidos"] += 1
                    if request.session["intentos_fallidos"] >= 5:
                        bloqueado_hasta = datetime.datetime.now() + datetime.timedelta(minutes=15)
                        request.session["bloqueado_hasta"] = bloqueado_hasta.isoformat()
                        messages.error(request, "Has superado los intentos. Intenta de nuevo en 15 minutos.")
                    else:
                        restantes = 5 - request.session["intentos_fallidos"]
                        messages.error(request, f"Documento no registrado. Intentos restantes: {restantes}")
    else:
        form = LoginForm()

    return render(request, "usuario/inicio_sesion.html", {"form": form})



def logout_view(request):
    logout(request)
    request.session.flush()
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('login')


@login_requerido
def perfil_usuario(request):
    usuario = getattr(request, 'usuario', None)
    if not usuario:
        return redirect('login')

    residente = None
    if usuario.id_rol.id_rol == 2:
        residente = get_object_or_404(DetalleResidente, cod_usuario=usuario)

    vehiculo = VehiculoResidente.objects.filter(cod_usuario=usuario).first()
    form_usuario = UsuarioUpdateForm(instance=usuario)
    form_vehiculo = VehiculoResidenteForm(instance=vehiculo)  # Inicializamos por defecto

    if request.method == 'POST':
        if 'vehiculo_submit' in request.POST:
            tipo_nuevo = request.POST.get('tipo_vehiculo')
            placa_nueva_raw = request.POST.get('placa', '').upper().strip().replace('-', '').replace(' ', '')
            placa_nueva_formateada = f"{placa_nueva_raw[:3]}-{placa_nueva_raw[3:]}" if len(placa_nueva_raw) >= 5 else placa_nueva_raw

            existente = VehiculoResidente.objects.filter(
                placa__iexact=placa_nueva_formateada
            ).exclude(cod_usuario=usuario).first()
            
            form_vehiculo = VehiculoResidenteForm(request.POST, instance=vehiculo or VehiculoResidente())

            if existente:
                messages.error(request, f"La placa {placa_nueva_formateada} ya está registrada por otro usuario.")
            elif form_vehiculo.is_valid():
                nuevo_vehiculo = form_vehiculo.save(commit=False)
                nuevo_vehiculo.cod_usuario = usuario
                if nuevo_vehiculo.activo is None:
                    nuevo_vehiculo.activo = True
                nuevo_vehiculo.save()
                messages.success(request, "Vehículo guardado correctamente.")
                return redirect('perfil_usuario')
            else:
                messages.error(request, "Error en el formulario de vehículo. Verifique los datos ingresados.")

        elif 'usuario_submit' in request.POST:
            form_usuario = UsuarioUpdateForm(request.POST, instance=usuario)
            if form_usuario.is_valid():
                form_usuario.save()
                messages.success(request, "Datos actualizados correctamente.")
                return redirect('perfil_usuario')

    # Actualizamos el vehículo para el template después del POST
    vehiculo = VehiculoResidente.objects.filter(cod_usuario=usuario).first()
    form_vehiculo = form_vehiculo or VehiculoResidenteForm(instance=vehiculo)

    return render(request, 'usuario/perfil.html', {
        'usuario': usuario,
        'residente': residente,
        'vehiculo': vehiculo,
        'vehiculos': [vehiculo] if vehiculo else [],
        'form_usuario': form_usuario,
        'form_vehiculo': form_vehiculo,
    })


@login_requerido
def cambiar_contrasena(request):
    if request.method == 'POST':
        nueva = request.POST.get('nueva_contraseña')
        confirmar = request.POST.get('confirmar_contraseña')

        if nueva and nueva == confirmar:
            errors = []
            if len(nueva) < 5:
                errors.append("Debe tener al menos 5 caracteres.")
            if not re.search(r"[A-Z]", nueva):
                errors.append("Debe tener al menos una letra mayúscula.")

            if errors:
                for e in errors:
                    messages.error(request, e)
            else:
                user = request.usuario
                user.contraseña = make_password(nueva)
                user.save()
                messages.success(request, "Contraseña actualizada correctamente.")
        else:
            messages.error(request, "Las contraseñas no coinciden.")

    return redirect('perfil_usuario')


def index(request):
    return render(request, 'usuario/index.html')


def solicitar_reset(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        documento = request.POST.get("documento")

        try:
            usuario = Usuario.objects.get(correo=correo, numero_documento=documento)
            token = usuario.generar_token_reset()
            reset_url = request.build_absolute_uri(
                reverse("reset_password", kwargs={"token": token})
            )

            send_mail(
                subject="Recuperar contraseña - Altos de Fontibón",
                message=f"Hola {usuario.nombres}, usa este enlace para restablecer tu contraseña:\n{reset_url}",
                from_email="altosdefontibon.cr@gmail.com",
                recipient_list=[usuario.correo],
            )

            messages.success(request, "Hemos enviado un enlace a tu correo.")
            return redirect("login")

        except Usuario.DoesNotExist:
            messages.error(
                request, 
                "No encontramos un usuario con ese correo y documento."
            )

    return render(request, "usuario/solicitar_reset.html")


def reset_password(request, token):
    try:
        usuario = Usuario.objects.get(reset_token=token)
    except Usuario.DoesNotExist:
        usuario = None

    if usuario and usuario.token_es_valido(token):
        if request.method == "POST":
            nueva = request.POST.get("nueva_contraseña")
            confirmar = request.POST.get("confirmar_contraseña")

            if not nueva or not confirmar:
                messages.error(request, "Debes ingresar y confirmar la nueva contraseña.")
                return render(request, "usuario/reset_password.html", {"token": token})

            if nueva != confirmar:
                messages.error(request, "Las contraseñas no coinciden.")
                return render(request, "usuario/reset_password.html", {"token": token})

            if not re.match(r'^(?=.*[A-Z]).{6,}$', nueva):
                messages.error(request, "La contraseña debe tener al menos 6 caracteres y una letra mayúscula.")
                return render(request, "usuario/reset_password.html", {"token": token})

            usuario.contraseña = make_password(nueva)
            usuario.reset_token = None
            usuario.reset_token_expira = None
            usuario.save()
            messages.success(request, "Tu contraseña fue restablecida con éxito. Ya puedes iniciar sesión.")
            return redirect("login")

        return render(request, "usuario/reset_password.html", {"token": token})
    else:
        messages.error(request, "El enlace no es válido o ya ha expirado.")
        return redirect("solicitar_reset")
