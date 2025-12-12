import re  
from django.shortcuts import render, redirect, get_object_or_404
from usuario.models import *
from .forms import *
from django.contrib import messages
from django.utils import timezone
from random import choice
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from usuario.decorators import *
from django.core.mail import send_mail
from django.urls import reverse
from .models import *
from reportlab.lib.pagesizes import letter
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from django.conf import settings
from usuario.utils import enviar_correo_async


@rol_requerido([4])
@login_requerido
def panel_general_vigilante(request):
    return render(request, "vigilante/panel.html")



def normalizar_placa(placa_raw):
    """
    Recibe una placa como string, la convierte a mayúsculas, agrega guion
    y valida formatos:
    - Carro: AAA-123
    - Moto: AAA-12A
    Retorna (placa_normalizada, tipo_vehiculo)
    """
    if not placa_raw:
        raise ValueError("No se proporcionó placa.")

    placa = placa_raw.upper().replace(" ", "").replace("-", "")

    if not re.match(r'^[A-Z0-9]+$', placa):
        raise ValueError("La placa solo puede contener letras y números.")

    # Carro
    if len(placa) == 6 and re.match(r'^[A-Z]{3}[0-9]{3}$', placa):
        return f"{placa[:3]}-{placa[3:]}", "Carro"

    # Moto
    elif len(placa) == 6 and re.match(r'^[A-Z]{3}[0-9]{2}[A-Z]$', placa):
        return f"{placa[:3]}-{placa[3:]}", "Moto"

    raise ValueError("Formato de placa inválido. Use AAA123 (carro) o AAA12A (moto).")


@rol_requerido([4])
@login_requerido
def registrar_parqueadero(request):
    from random import choice
    from django.utils import timezone
    from datetime import datetime, timedelta

    query_raw = request.GET.get("placa", "")
    accion = request.GET.get("accion")

    query = None
    tipo_vehiculo_detectado = None

    # Normalizar placa si hay función disponible
    if query_raw:
        try:
            query, tipo_vehiculo_detectado = normalizar_placa(query_raw)
        except Exception as e:
            messages.error(request, f"Error al normalizar placa: {e}")
            query = None

    registros = DetallesParqueadero.objects.select_related(
        "id_visitante", "id_vehiculo_residente", "id_parqueadero"
    ).order_by('-id_detalle')

    placa_encontrada = None
    mostrar_formulario = False
    mostrar_modal_residente = False
    form = None

    # ----------------------------------------------------
    # POST: Registrar visitante
    # ----------------------------------------------------
    if request.method == "POST" and "guardar_visitante" in request.POST:
        form = VisitanteForm(request.POST)
        if form.is_valid():
            visitante = form.save()

            detalle = DetalleResidente.objects.filter(
                torre=visitante.torre,
                apartamento=visitante.apartamento
            ).select_related("cod_usuario").first()

            if detalle and detalle.cod_usuario and detalle.cod_usuario.correo:
                try:
                    enviar_correo_async(
                        subject="Nuevo visitante registrado - Altos de Fontibón",
                        message=(
                            f"Estimado(a) {detalle.cod_usuario.nombres},\n\n"
                            f"Se ha registrado un visitante para su apartamento.\n\n"
                            f"Visitante: {visitante.nombres} {visitante.apellidos}\n"
                            f"Documento: {visitante.documento}\n"
                            f"Celular: {visitante.celular}\n"
                            f"Vehículo: {visitante.tipo_vehiculo} - {visitante.placa}\n\n"
                            "Atentamente,\nAdministración"
                        ),
                        from_email="altosdefontibon.cr@gmail.com",
                        recipient_list=[detalle.cod_usuario.correo]
                    )
                except Exception:
                    pass

            parqueaderos_disp = Parqueadero.objects.filter(estado=False)
            if not parqueaderos_disp.exists():
                messages.error(request, "No hay parqueadero disponible.")
                return redirect('registrar_detalle_parqueadero')

            parqueadero_default = choice(parqueaderos_disp)
            parqueadero_default.estado = True
            parqueadero_default.save()

            DetallesParqueadero.objects.create(
                tipo_propietario="Visitante",
                id_visitante=visitante,
                id_parqueadero=parqueadero_default,
                hora_llegada=timezone.localtime().time()
            )

            messages.success(request, f"Visitante creado con placa {visitante.placa}")
            return redirect('registrar_detalle_parqueadero')

        mostrar_formulario = True

    # ----------------------------------------------------
    # GET: Lógica principal
    # ----------------------------------------------------
    if query:
        try:
            vehiculo = VehiculoResidente.objects.filter(placa=query).first()
            visitante = Visitante.objects.filter(placa=query).first()
            hora_actual = timezone.localtime().time()

            # -----------------------------------------------
            # RESIDENTE (verifica sorteo y entrada/salida)
            # -----------------------------------------------
            if vehiculo:

                # Obtener el último sorteo REAL
                ultimo_sorteo = Sorteo.objects.order_by('-id_sorteo').first()
                if not ultimo_sorteo:
                    messages.error(request, "No hay sorteos registrados.")
                    return redirect('registrar_detalle_parqueadero')

                if not vehiculo.cod_usuario:
                    messages.error(request, f"El vehículo {query} no tiene usuario asociado.")
                    return redirect('registrar_detalle_parqueadero')

                detalle_residente = DetalleResidente.objects.filter(
                    cod_usuario=vehiculo.cod_usuario
                ).first()

                if not detalle_residente:
                    messages.error(request, f"No se encontró DetalleResidente para este vehículo.")
                    return redirect('registrar_detalle_parqueadero')

                ganador = GanadorSorteo.objects.filter(
                    id_sorteo=ultimo_sorteo,
                    id_detalle_residente=detalle_residente
                ).select_related("id_parqueadero").first()

                if not ganador:
                    messages.error(request, "Este vehículo NO es ganador del último sorteo.")
                    return redirect('registrar_detalle_parqueadero')

                parqueadero_ganador = ganador.id_parqueadero
                placa_encontrada = vehiculo.placa

                # Buscar si tiene una entrada activa
                entrada_activa = DetallesParqueadero.objects.filter(
                    id_vehiculo_residente=vehiculo,
                    hora_salida__isnull=True
                ).first()

                # ----------------------------------------------------
                # MOSTRAR MODAL ANTES DE ENTRADA O SALIDA
                # ----------------------------------------------------
                if not accion:
                    mostrar_modal_residente = True

                # ----------------------------------------------------
                # ENTRADA
                # ----------------------------------------------------
                elif accion == "entrada":
                    if entrada_activa:
                        messages.error(request, "Este vehículo ya tiene una entrada activa.")
                        return redirect('registrar_detalle_parqueadero')

                    if not parqueadero_ganador.estado:
                        parqueadero_ganador.estado = True
                        parqueadero_ganador.save()

                    DetallesParqueadero.objects.create(
                        tipo_propietario="Residente",
                        id_vehiculo_residente=vehiculo,
                        id_parqueadero=parqueadero_ganador,
                        hora_llegada=hora_actual
                    )

                    messages.success(request, "Entrada registrada correctamente.")
                    return redirect('registrar_detalle_parqueadero')

                # ----------------------------------------------------
                # SALIDA
                # ----------------------------------------------------
                elif accion == "salida":
                    if not entrada_activa:
                        messages.error(request, "Este vehículo NO tiene una entrada registrada.")
                        return redirect('registrar_detalle_parqueadero')

                    entrada_activa.hora_salida = hora_actual
                    entrada_activa.save()

                    parqueadero_ganador.estado = False
                    parqueadero_ganador.save()

                    messages.success(request, "Salida registrada correctamente.")
                    return redirect('registrar_detalle_parqueadero')

            # -----------------------------------------------
            # VISITANTE EXISTENTE
            # -----------------------------------------------
            elif visitante:
                parqueaderos_disp = Parqueadero.objects.filter(estado=False)
                if parqueaderos_disp.exists():
                    parqueadero_default = choice(parqueaderos_disp)
                    parqueadero_default.estado = True
                    parqueadero_default.save()

                    DetallesParqueadero.objects.create(
                        tipo_propietario="Visitante",
                        id_visitante=visitante,
                        id_parqueadero=parqueadero_default,
                        hora_llegada=hora_actual
                    )

                    messages.success(request, f"Detalle creado para visitante {visitante.placa}")
                    return redirect('registrar_detalle_parqueadero')
                else:
                    messages.error(request, "No hay parqueaderos disponibles para visitantes.")

            # -----------------------------------------------
            # VISITANTE NUEVO
            # -----------------------------------------------
            else:
                mostrar_formulario = True
                if form is None:
                    form = VisitanteForm(initial={
                        "placa": query,
                        "tipo_vehiculo": tipo_vehiculo_detectado
                    })

        except Exception as e:
            messages.error(request, f"Error inesperado: {e}")
            print("Error registrar_parqueadero:", e)
            return redirect('registrar_detalle_parqueadero')

    # ----------------------------------------------------
    # Cálculo tiempos/pagos
    # ----------------------------------------------------
    for detalle in registros:
        if detalle.tipo_propietario == "Residente":
            detalle.valor_pago = 0
            detalle.tiempo_total = None
            detalle.tiempo_total_str = None
        elif detalle.hora_llegada and detalle.hora_salida:
            llegada_dt = datetime.combine(detalle.registro, detalle.hora_llegada)
            salida_dt = datetime.combine(detalle.registro, detalle.hora_salida)
            if salida_dt < llegada_dt:
                salida_dt += timedelta(days=1)
            duracion = salida_dt - llegada_dt

            # ✅ Formatear sin milisegundos
            total_segundos = int(duracion.total_seconds())
            horas = total_segundos // 3600
            minutos = (total_segundos % 3600) // 60
            segundos = total_segundos % 60
            detalle.tiempo_total_str = f"{horas}:{minutos:02d}:{segundos:02d}"

            detalle.valor_pago = round(max(total_segundos / 3600, 1) * 2000, 2)
        else:
            detalle.tiempo_total = None
            detalle.valor_pago = None
            detalle.tiempo_total_str = None

    return render(request, "vigilante/parqueadero/vigilante.html", {
        "registros": registros,
        "placa_encontrada": placa_encontrada,
        "mostrar_formulario": mostrar_formulario,
        "mostrar_modal_residente": mostrar_modal_residente,
        "form": form,
    })


@rol_requerido([4])
@login_requerido
def poner_hora_salida(request, id_detalle):
    detalle = get_object_or_404(DetallesParqueadero, id_detalle=id_detalle)
    if not detalle.hora_salida:
        detalle.hora_salida = timezone.localtime().time()

        # Calcular tiempo total y valor a pagar
        llegada_dt = datetime.combine(detalle.registro, detalle.hora_llegada)
        salida_dt = datetime.combine(detalle.registro, detalle.hora_salida)

        if salida_dt < llegada_dt:
            salida_dt += timedelta(days=1)

        duracion = salida_dt - llegada_dt
        horas = duracion.total_seconds() / 3600

        detalle.tiempo_total = duracion
        detalle.valor_pago = round(max(horas, 1) * 2000, 2)
        detalle.save()

        messages.success(request, "Hora de salida registrada. Tiempo y valor calculados.")
    else:
        messages.info(request, "Este registro ya tiene hora de salida.")
    return redirect('registrar_detalle_parqueadero')


@rol_requerido([4])
@login_requerido
def realizar_pago(request, id_detalle):
    detalle = get_object_or_404(DetallesParqueadero, id_detalle=id_detalle)
    if detalle.hora_salida and detalle.pago is None:
        llegada_dt = datetime.combine(detalle.registro, detalle.hora_llegada)
        salida_dt = datetime.combine(detalle.registro, detalle.hora_salida)

        if salida_dt < llegada_dt:
            salida_dt += timedelta(days=1)

        duracion = salida_dt - llegada_dt
        horas = duracion.total_seconds() / 3600
        detalle.pago = round(max(horas, 1) * 2000, 2)
        detalle.tiempo_total = duracion
        detalle.save()

        parqueadero = detalle.id_parqueadero
        parqueadero.estado = False
        parqueadero.save()

        messages.success(request, f"Pago realizado: {detalle.pago} pesos")
    return redirect('registrar_detalle_parqueadero')


@rol_requerido([4])
@login_requerido
def registro_correspondencia_view(request):
    registros = RegistroCorrespondencia.objects.all()
    form = RegistroCorrespondenciaForm(request.POST or None)

    if request.method == 'POST' and 'crear_registro' in request.POST:
        if form.is_valid():
            registro = form.save(commit=False)

            # ⚡ Asignar fecha actual automáticamente
            registro.fecha_registro = timezone.localtime()
            registro.save()

            # Notificar a residentes
            residentes = Usuario.objects.filter(id_rol=2, estado="Activo")  
            for residente in residentes:
                try:
                    enviar_correo_async(
                        subject="Nuevo recibo en porteria - Altos de Fontibón",
                        message=(
                            f"Estimado residente \n\n"
                            f"Se ha registrado un nuevo recibo en la porteria del conjunto \n\n"
                            f"Descripción: {registro.descripcion}\n"
                            f"Fecha: {registro.fecha_registro.strftime('%d/%m/%Y %H:%M')}\n\n"
                            f"Por favor acérquese a reclamarlo en porteria\n\n"
                            f"Atentamente.\nAdministración: Altos de Fontibón"
                        ),
                        from_email="altosdefontibon.cr@gmail.com",
                        recipient_list=[residente.correo]
                    )
                except Exception as e:
                    print(f"Error enviando a {residente.correo}: {e}")

            messages.success(request, "Registro de correspondencia creado y notificación enviada a los residentes.")
            return redirect('registro_correspondencia')

    form_entrega = BuscarResidenteForm()  
    return render(request, 'vigilante/correspondecia/resibos.html', {
        'registros': registros,
        'form': form,
        'form_entrega': form_entrega
    })



@rol_requerido([4])
@login_requerido
def registrar_entrega_view(request):
    # ============================================================
    # REGISTRAR ENTREGA DE PAQUETE / RECIBO
    # ============================================================
    if request.method == "POST" and request.POST.get("accion") == "registrar_entrega":

        id_corres = request.POST.get("id_correspondencia")
        id_res = request.POST.get("id_residente")

        residente = get_object_or_404(DetalleResidente, id_detalle_residente=id_res)
        correspondencia = get_object_or_404(RegistroCorrespondencia, id_correspondencia=id_corres)

        # Evitar duplicados
        if not EntregaCorrespondencia.objects.filter(
            id_detalle_residente=residente,
            id_correspondencia=correspondencia
        ).exists():

            EntregaCorrespondencia.objects.create(
                id_usuario=request.usuario,
                id_correspondencia=correspondencia,
                id_detalle_residente=residente,
                fecha_entrega=timezone.now()
            )

        return JsonResponse({"success": True})

    # ============================================================
    # FILTRADO AJAX: BUSCAR REGISTROS PENDIENTES
    # ============================================================
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":

        torre = request.POST.get("torre")
        apartamento = request.POST.get("apartamento")

        # Validación rápida
        if not torre or not apartamento:
            return JsonResponse({
                "html": "<div class='alert alert-warning'>Debe seleccionar torre y apartamento.</div>"
            })

        # Buscar residente
        try:
            residente = DetalleResidente.objects.get(torre=torre, apartamento=apartamento)
        except DetalleResidente.DoesNotExist:
            return JsonResponse({
                "html": "<div class='alert alert-danger'>No se encontró un residente con esos datos.</div>"
            })

        # Obtener IDs de correspondencia ya entregada
        entregados_ids = EntregaCorrespondencia.objects.filter(
            id_detalle_residente=residente
        ).values_list("id_correspondencia_id", flat=True)

        # Registros sin entregar
        registros = RegistroCorrespondencia.objects.exclude(
            id_correspondencia__in=entregados_ids
        )

        # Render parcial corregido
        html = render_to_string(
            "vigilante/correspondecia/partial_registros.html",
            {"registros": registros, "residente": residente}
        )

        return JsonResponse({"html": html})

    # ============================================================
    # Si llega aquí → petición inválida
    # ============================================================
    return JsonResponse({"success": False})


@rol_requerido([4])
@login_requerido
def buscar_paquete(request):
    apartamento = request.GET.get('apartamento')
    torre = request.GET.get('torre')

    # Solo mostrar paquetes no entregados
    paquetes = Paquete.objects.filter(fecha_entrega__isnull=True)

    if apartamento:
        paquetes = paquetes.filter(apartamento=apartamento)
    if torre:
        paquetes = paquetes.filter(torre=torre)

    resultados = []
    for p in paquetes:
        resultados.append({
            "id": p.id_paquete,
            "fecha_recepcion": p.fecha_recepcion.strftime("%d/%m/%Y"),
            "vigilante_recepcion": f"{p.cod_usuario_recepcion.nombres} {p.cod_usuario_recepcion.apellidos}",
        })

    return JsonResponse({"resultados": resultados})


@rol_requerido([4])
@login_requerido
def correspondencia(request):
    paquetes = Paquete.objects.select_related('cod_usuario_recepcion', 'cod_usuario_entrega')\
                              .order_by("-fecha_recepcion")

    vigilantes = Usuario.objects.filter(id_rol=4, estado='Activo').order_by('nombres')

    registrar_form = RegistrarPaqueteForm()
    entrega_form = EntregaPaqueteForm()

    return render(request, "vigilante/correspondecia/correspondencia.html", {
        "paquetes": paquetes,
        "vigilantes": vigilantes,
        "registrar_form": registrar_form,
        "entrega_form": entrega_form,
    })


@rol_requerido([4])
@login_requerido
def registrar_paquete(request):
    if request.method == 'POST':
        form = RegistrarPaqueteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            paquete = Paquete(
                apartamento=data['apartamento'],
                torre=data['torre'],
                descripcion=data.get('descripcion') or None,
                fecha_recepcion=timezone.now(),
                cod_usuario_recepcion=data['cod_usuario_recepcion']
            )
            paquete.save()

            detalle = DetalleResidente.objects.filter(
                torre=paquete.torre,
                apartamento=paquete.apartamento
            ).select_related("cod_usuario").first()

            if detalle and detalle.cod_usuario and detalle.cod_usuario.correo:
                try:
                    enviar_correo_async(
                        subject="Nuevo paquete en porteria - Altos de Fontibón",
                        message=(
                            f"Estimado(a) {detalle.cod_usuario.nombres},\n\n"
                            f"Se ha registrado un paquete para su apartamento {paquete.apartamento}, Torre {paquete.torre}\n\n"
                            f"Descripción: {paquete.descripcion or 'Sin descripción'}\n\n"
                            "Puede acercarse a porteria a reclamarlo\n\n"
                            "Atentamente.\nAdministración: Altos de Fontibón"
                        ),
                        from_email="altosdefontibon.cr@gmail.com",
                        recipient_list=[detalle.cod_usuario.correo]
                    )
                except Exception as e:
                    print(f"Error enviando correo a {detalle.cod_usuario.correo}: {e}")
            else:
                print("No se encontró residente con ese apartamento y torre.")

            messages.success(request, "Paquete registrado correctamente y notificación enviada.")
        else:
            messages.error(request, "Revise los datos del formulario.")

    return redirect(reverse('correspondencia'))


@rol_requerido([4])
@login_requerido
def entregar_paquete(request):
    if request.method == 'POST':
        form = EntregaPaqueteForm(request.POST, request.FILES)  
        if form.is_valid():
            id_paquete = form.cleaned_data['id_paquete']
            nombre_residente = form.cleaned_data['nombre_residente']
            vigilante_entrega = form.cleaned_data['cod_usuario_entrega']
            foto_cedula = form.cleaned_data['foto_cedula']  

            paquete = get_object_or_404(Paquete, pk=id_paquete)
            paquete.nombre_residente = nombre_residente
            paquete.cod_usuario_entrega = vigilante_entrega
            paquete.fecha_entrega = timezone.now()

            if foto_cedula:
                paquete.foto_cedula = foto_cedula  

            paquete.save()
            messages.success(request, "Entrega registrada correctamente.")
        else:
            # Revisamos específicamente el error de 'nombre_residente'
            if 'nombre_residente' in form.errors:
                messages.error(request, "No se puede poner números ni símbolos en 'Recibido Por'.")
            else:
                messages.error(request, "Revise los datos del formulario de entrega.")
    return redirect(reverse('correspondencia'))


@rol_requerido([4])
@login_requerido
def novedades_view(request):
    usuarios_rol4 = Usuario.objects.filter(id_rol=4)
    paquetes_no_entregados = Paquete.objects.filter(fecha_entrega__isnull=True)
    visitantes = Visitante.objects.all()

    if request.method == "POST":
        form = NovedadesForm(request.POST, request.FILES)

        if not form.is_valid():
            messages.error(request, "Todos los campos deben estar llenos.")
        else:
            tipo_novedad = form.cleaned_data.get("tipo_novedad")
            descripcion = form.cleaned_data.get("descripcion", "")
            foto = form.cleaned_data.get("foto", None)
            vigilante = form.cleaned_data.get("id_usuario")

            novedad_data = {
                "descripcion": descripcion,
                "foto": foto,
                "id_usuario": vigilante,
                "id_detalle_residente": None,
                "id_paquete": None,
                "id_visitante": None,
            }

            # ============================
            # NOVEDAD POR PAQUETE
            # ============================
            if tipo_novedad == "paquete":
                paquete = form.cleaned_data.get("id_paquete")

                if paquete:
                    detalle_residente = DetalleResidente.objects.filter(
                        apartamento=paquete.apartamento,
                        torre=paquete.torre
                    ).first()

                    novedad_data["id_paquete"] = paquete
                    novedad_data["id_detalle_residente"] = detalle_residente

            # ============================
            # NOVEDAD POR VISITANTE
            # ============================
            elif tipo_novedad == "visitante":
                visitante = form.cleaned_data.get("id_visitante")

                if visitante:
                    detalle_residente = DetalleResidente.objects.filter(
                        apartamento=visitante.apartamento,
                        torre=visitante.torre
                    ).first()

                    novedad_data["id_visitante"] = visitante
                    novedad_data["id_detalle_residente"] = detalle_residente

            Novedades.objects.create(**novedad_data)

            messages.success(request, "Novedad registrada correctamente.")
            return redirect("novedades")

    else:
        form = NovedadesForm()

    novedades = Novedades.objects.all().order_by("-fecha")

    context = {
        "form": form,
        "novedades": novedades,
        "usuarios_rol4": usuarios_rol4,
        "paquetes": paquetes_no_entregados,
        "visitantes": visitantes,
    }
    return render(request, "vigilante/novedades/listar_novedades.html", context)




@rol_requerido([4])
@login_requerido
def menu_reporte_parqueadero(request):
    """
    Muestra un menú para generar el PDF del reporte de parqueadero con filtros.
    """
    # Datos dinámicos para el formulario
    anios = range(2023, datetime.now().year + 1)  # Años desde 2023 hasta el actual
    meses = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
        (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
        (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
    ]
    dias = range(1, 32)

    context = {
        "anios": anios,
        "meses": meses,
        "dias": dias
    }
    return render(request, "vigilante/parqueadero/menu_reporte_parqueadero.html", context)


@rol_requerido([4])
@login_requerido
def reporte_visitantes_pdf(request):
    # Parámetros de filtrado desde la URL
    dia = request.GET.get("dia")
    mes_inicio = request.GET.get("mes_inicio")
    mes_fin = request.GET.get("mes_fin")
    anio = request.GET.get("anio")
    
    # Nuevos parámetros para los formularios actualizados
    fecha = request.GET.get("fecha")
    mes = request.GET.get("mes")
    
    # Procesar fecha si se proporciona
    if fecha:
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
            dia = fecha_obj.day
            mes_inicio = fecha_obj.month
            anio = fecha_obj.year
        except ValueError:
            pass
    
    # Procesar mes individual si se proporciona
    if mes and anio:
        mes_inicio = mes
        mes_fin = mes

    # Respuesta como PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="reporte_visitantes.pdf"'

    # Documento
    doc = SimpleDocTemplate(response, pagesize=letter,
                           leftMargin=50, rightMargin=50,
                           topMargin=70, bottomMargin=70)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()

    COLOR_PRIMARIO = colors.HexColor('#065F46')
    COLOR_SECUNDARIO = colors.HexColor('#059669')
    COLOR_FONDO_CLARO = colors.HexColor('#F0FDF4')

    estilo_titulo_principal = ParagraphStyle(
        'TituloPrincipal',
        parent=styles['Heading1'],
        fontSize=22,
        spaceAfter=25,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    estilo_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    estilo_encabezado_tabla = ParagraphStyle(
        'EncabezadoTabla',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    estilo_celda_tabla = ParagraphStyle(
        'CeldaTabla',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    estilo_celda_destacada = ParagraphStyle(
        'CeldaDestacada',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    estilo_info_fecha = ParagraphStyle(
        'InfoFecha',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_RIGHT,
        fontName='Helvetica'
    )

    # Logo
    logo_path = "static/img/Logo Fontibon.png"
    try:
        logo = Image(logo_path, width=140, height=60)
        logo.hAlign = 'LEFT'
    except:
        logo = Paragraph("", styles['Normal'])

    # Fecha y hora actual
    fecha_reporte = datetime.now().strftime("%d/%m/%Y")
    hora_reporte = datetime.now().strftime("%H:%M")
    info_fecha = Paragraph(f"<b>Generado:</b><br/>{fecha_reporte}<br/>{hora_reporte}", estilo_info_fecha)

    # Encabezado
    titulo_principal = Paragraph("REPORTE DE PARQUEADERO", estilo_titulo_principal)
    subtitulo = Paragraph("Control de Visitantes", estilo_subtitulo)
    header_data = [[logo, [titulo_principal, subtitulo], info_fecha]]
    header_table = Table(header_data, colWidths=[120, 300, 130])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
    ]))
    elements.append(header_table)

    # Línea
    line_table = Table([['']], colWidths=[500])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 3, COLOR_SECUNDARIO),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 25))

    # Encabezados tabla
    encabezados = ["Fecha", "Nombre del Visitante", "Placa", "Pago"]
    data = [[Paragraph(encab, estilo_encabezado_tabla) for encab in encabezados]]

    # Filtrado de datos
    registros = DetallesParqueadero.objects.select_related("id_visitante").filter(
        tipo_propietario="Visitante"
    ).order_by("-id_detalle")

    # CORRECCIÓN: Usar filtros directos para DateField (sin __date)
    if dia and mes_inicio and anio:
        # Filtrar fecha exacta - CORREGIDO
        fecha_filtro = datetime(int(anio), int(mes_inicio), int(dia)).date()
        registros = registros.filter(registro=fecha_filtro)
    else:
        if anio:
            registros = registros.filter(registro__year=anio)
        if mes_inicio and mes_fin:
            registros = registros.filter(registro__month__gte=mes_inicio, registro__month__lte=mes_fin)
        elif mes_inicio:
            registros = registros.filter(registro__month=mes_inicio)

    # Contadores
    total_visitantes = 0
    total_ingresos = 0

    for detalle in registros:
        if detalle.id_visitante:
            fecha = detalle.registro.strftime("%d/%m/%Y")
            nombre = f"{detalle.id_visitante.nombres} {detalle.id_visitante.apellidos}"
            placa = detalle.id_visitante.placa.upper()
            pago = detalle.pago if detalle.pago else 0
            pago_formateado = f"$ {pago:,.0f}" if pago > 0 else "Sin pago"

            data.append([
                Paragraph(fecha, estilo_celda_tabla),
                Paragraph(nombre, estilo_celda_tabla),
                Paragraph(placa, estilo_celda_tabla),
                Paragraph(pago_formateado, estilo_celda_destacada if pago > 0 else estilo_celda_tabla)
            ])

            total_visitantes += 1
            total_ingresos += pago

    # Tabla principal
    table = Table(data, colWidths=[85, 200, 85, 85], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARIO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor('#D1FAE5')),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_FONDO_CLARO]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 25))

    # Resumen
    resumen_data = [
        [" RESUMEN DEL REPORTE", ""],
        [f"Total de visitantes registrados:", f"{total_visitantes}"],
        [f"Ingresos totales generados:", f"$ {total_ingresos:,.0f}"]
    ]
    resumen_table = Table(resumen_data, colWidths=[200, 100])
    resumen_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_SECUNDARIO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor('#D1FAE5')),
    ]))
    elements.append(resumen_table)
    elements.append(Spacer(1, 30))

    # Pie de página
    footer_style = ParagraphStyle('Footer', fontSize=8, alignment=TA_CENTER, fontName='Helvetica')
    footer_text = f"Sistema de Parqueadero • Reporte generado el {fecha_reporte} a las {hora_reporte}"
    elements.append(Paragraph(footer_text, footer_style))

    # Construir PDF
    doc.build(elements)
    return response