from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from api.models import Reservacion, ReservacionInvitado, SalaJuntas,Invitado,Area
from api.filters import ReservacionFilter  
from datetime import datetime, timedelta, date
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import calendar
from django.contrib import messages
from django.views.decorators.http import require_POST


def administracion(request):
    # Obtener todas las salas
    salas = SalaJuntas.objects.all()

    # Verificar si se requiere filtrar por fecha actual/futura
    filtro_fecha = request.GET.get('fecha')
    reservaciones = Reservacion.objects.all().order_by('fecha', 'hora_inicio')

    if filtro_fecha == 'actuales_y_futuras':
        reservaciones = reservaciones.filter(fecha__gte=date.today())

    # Aplicar filtro personalizado
    myFilter = ReservacionFilter(request.GET, queryset=reservaciones)
    reservaciones = myFilter.qs

    # Calcular si cada reservación puede ser editada o eliminada
    ahora = datetime.now()
    for reservacion in reservaciones:
        inicio = datetime.combine(reservacion.fecha, reservacion.hora_inicio)
        puede_modificar = inicio > ahora + timedelta(hours=1)
        reservacion.editable = puede_modificar
        reservacion.eliminable = puede_modificar

    # Cargar áreas con invitados (para el modal de gestión)
    areas = Area.objects.prefetch_related('invitados').all()

    if request.method == 'POST' and 'eliminar_reservacion' in request.POST:
        pk = request.POST.get('id_reservacion')
        motivo = request.POST.get('motivo')
        reservacion = get_object_or_404(Reservacion, id_reservacion=pk)

        # Enviar correo a invitados
        invitados = Invitado.objects.filter(reservacioninvitado__reservacion=reservacion)
        for invitado in invitados:
            subject = f"Reservación eliminada: {reservacion.evento}"
            message = f"""
                <h2>🗑️ Confirmación de Eliminación de Reservación</h2>
                <p>La reservación para <strong>{reservacion.evento}</strong> ha sido eliminada.</p>
                <h3>Detalles de la Reservación eliminada:</h3>
                <ul>
                    <li>📆 Fecha: {reservacion.fecha}</li>
                    <li>🕒 Hora de inicio: {reservacion.hora_inicio}</li>
                    <li>🕒 Hora de fin: {reservacion.hora_final}</li>
                    <li>🏢 Sala: {reservacion.sala}</li>
                </ul>
                <p>Motivo de eliminación: <strong>{motivo}</strong></p>
                <p>Atentamente,</p>
                <p>{request.user.username}</p>
            """
            send_mail(subject, "", 'informatica.cdt.stc@gmail.com', [invitado.correo], html_message=message)

        reservacion.delete()
        return redirect(request.get_full_path())

    # Contexto para la plantilla
    context = {
        'reservaciones': reservaciones,
        'myFilter': myFilter,
        'salas': salas,
        'areas': areas,  # Necesario para mostrar opciones en el modal de gestión de invitaciones,
    }

    return render(request, 'administracion.html', context)



from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from datetime import datetime
from api.isc import generar_ics

@login_required
def Periodicamente(request):
    salas = SalaJuntas.objects.all()

    if request.method == 'POST':
        fechas_str = request.POST.getlist('fechas_validas[]')
        if not fechas_str:
            messages.error(request, "No se seleccionó ninguna fecha válida.")
            return redirect('periodica')

        sala = SalaJuntas.objects.get(id_sala=request.POST.get('sala'))
        evento = request.POST.get('evento')
        comentarios = request.POST.get('comentarios')
        hora_inicio = datetime.strptime(request.POST.get('hora_inicio'), "%H:%M").time()
        hora_final = datetime.strptime(request.POST.get('hora_final'), "%H:%M").time()

        fechas = [datetime.strptime(f, "%Y-%m-%d").date() for f in fechas_str]

        # Guardar reservaciones
        reservas = [
            Reservacion(
                evento=evento,
                comentarios=comentarios,
                fecha=f,
                hora_inicio=hora_inicio,
                hora_final=hora_final,
                sala=sala,
                usuario=request.user
            )
            for f in fechas
        ]
        Reservacion.objects.bulk_create(reservas)

        # Generar archivo ICS con evento recurrente
        archivo_ics = generar_ics(
            evento=evento,
            sala=sala.nombre,
            comentarios=comentarios,
            fechas=fechas,
            hora_inicio=hora_inicio,
            hora_fin=hora_final,
            organizador_email=request.user.email
        )

        # Enviar correo al organizador (por ahora solo a él)
        email = EmailMessage(
            subject=f"Reservación confirmada: {evento}",
            body="Adjunto encontrarás el evento para añadirlo a tu calendario.",
            from_email="eliasaranda828@gmail.com",
            to=["eliasaranda828@gmail.com"]

        )

        if archivo_ics:
            email.attach("evento_reservado.ics", archivo_ics.read(), "text/calendar")
            print("Adjuntando archivo:", archivo_ics is not None)
            print("Enviando a:", email.to)

        email.send()

        messages.success(request, f"Se crearon {len(reservas)} reservaciones exitosamente y se envió el evento al calendario.")
        return redirect('periodica')

    return render(request, "reservation_periodica.html", {"salas": salas})



@require_POST
def ValidadrFechas(request):
    evento = request.POST.get('evento')
    sala_id = request.POST.get('sala')
    mes_nombre = request.POST.get('mes')
    dias = request.POST.getlist('dias')
    h_inicio = request.POST.get('hora_inicio')
    h_final = request.POST.get('hora_final')

    if not (evento and sala_id and mes_nombre and dias and h_inicio and h_final):
        return JsonResponse({'error': 'Faltan datos'}, status=400)

    meses = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
        "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }

    mes = meses.get(mes_nombre.lower())
    if not mes:
        return JsonResponse({'error': 'Mes inválido'}, status=400)

    año = datetime.now().year
    dias_map = {
        "lunes": 0, "martes": 1, "miércoles": 2, "jueves": 3, "viernes": 4
    }

    fechas = []
    hoy = date.today()
    for semana in calendar.monthcalendar(año, mes):
        for dia in dias:
            idx = dias_map[dia.lower()]
            if semana[idx] != 0:
                posible_fecha = date(año, mes, semana[idx])
                if posible_fecha >= hoy:
                    fechas.append(posible_fecha)

    hora_inicio = datetime.strptime(h_inicio, "%H:%M").time()
    hora_final = datetime.strptime(h_final, "%H:%M").time()

    sala = SalaJuntas.objects.get(id_sala=sala_id)

    disponibles = []
    conflictos = []

    for f in fechas:
        solapadas = Reservacion.objects.filter(
            fecha=f,
            sala=sala,
            hora_inicio__lt=hora_final,
            hora_final__gt=hora_inicio
        )
        if solapadas.exists():
            for r in solapadas:
                conflictos.append({
                    'fecha': f.strftime("%d %B %Y"),
                    'evento': r.evento,
                    'inicio': r.hora_inicio.strftime("%H:%M"),
                    'fin': r.hora_final.strftime("%H:%M")
                })
        else:
            disponibles.append(f.strftime("%Y-%m-%d"))  # ejemplo: '2025-06-04'


    return JsonResponse({
        'disponibles': disponibles,
        'conflictos': conflictos
    })


from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

def monitor_sala(request, nombre_sala):
    sala = get_object_or_404(SalaJuntas, nombre=nombre_sala)

    hoy = timezone.now().date()
    primer_dia_mes = hoy.replace(day=1)
    ultimo_dia_mes = primer_dia_mes.replace(day=calendar.monthrange(hoy.year, hoy.month)[1])

    # Crear lista con todos los días del mes
    dias_mes = [primer_dia_mes + timedelta(days=i) for i in range((ultimo_dia_mes - primer_dia_mes).days + 1)]

    return render(request, 'calendario_cl.html', {
        'sala': sala,
        'dias_mes': dias_mes,
        'primer_dia_mes': primer_dia_mes,
        'ultimo_dia_mes': ultimo_dia_mes,
    })
from django.http import JsonResponse

def api_reservaciones_sala(request, nombre_sala):
    sala = SalaJuntas.objects.get(nombre=nombre_sala)

    primer_dia_mes = request.GET.get('inicio')
    ultimo_dia_mes = request.GET.get('fin')

    from datetime import datetime
    formato_fecha = '%Y-%m-%d'

    try:
        inicio = datetime.strptime(primer_dia_mes, formato_fecha).date()
        fin = datetime.strptime(ultimo_dia_mes, formato_fecha).date()
    except Exception:
        hoy = timezone.now().date()
        inicio = hoy.replace(day=1)
        fin = inicio.replace(day=calendar.monthrange(inicio.year, inicio.month)[1])

    reservaciones = Reservacion.objects.filter(
        sala=sala,
        fecha__range=(inicio, fin)
    ).order_by('fecha', 'hora_inicio')

    data = []
    for r in reservaciones:
        duracion_minutos = (datetime.combine(r.fecha, r.hora_final) - datetime.combine(r.fecha, r.hora_inicio)).seconds // 60
        data.append({
            'evento': r.evento,
            'fecha': r.fecha.strftime('%Y-%m-%d'),
            'inicio': r.hora_inicio.strftime('%H:%M'),
            'final': r.hora_final.strftime('%H:%M'),
            'duracion': duracion_minutos
        })

    return JsonResponse({'reservaciones': data})
