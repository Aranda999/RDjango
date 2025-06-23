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




@login_required
def Periodicamente(request):
    salas = SalaJuntas.objects.all()

    if request.method == 'POST':
        # Traer datos confirmados desde el formulario
        fechas_str = request.POST.getlist('fechas_validas[]')  # ← de JS
        if not fechas_str:
            messages.error(request, "No se seleccionó ninguna fecha válida.")
            return redirect('periodica')

        sala = SalaJuntas.objects.get(id_sala=request.POST.get('sala'))
        evento = request.POST.get('evento')
        comentarios = request.POST.get('comentarios')
        hora_inicio = datetime.strptime(request.POST.get('hora_inicio'), "%H:%M").time()
        hora_final = datetime.strptime(request.POST.get('hora_final'), "%H:%M").time()

        fechas = [datetime.strptime(f, "%Y-%m-%d").date() for f in fechas_str]

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
        messages.success(request, f"Se crearon {len(reservas)} reservaciones exitosamente.")
        return redirect('periodica')

    return render(request, "reservation_periodica.html", {"salas": salas})



@require_POST
def validar_periodicas(request):
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
    for semana in calendar.monthcalendar(año, mes):
        for dia in dias:
            idx = dias_map[dia.lower()]
            if semana[idx] != 0:
                fechas.append(date(año, mes, semana[idx]))

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
