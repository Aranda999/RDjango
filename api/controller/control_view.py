from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from api.models import Reservacion, ReservacionInvitado, SalaJuntas,Invitado,Area
from api.filters import ReservacionFilter  
from datetime import datetime, timedelta, date
from django.core.mail import send_mail
from datetime import datetime, timedelta, date
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail

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

    # Contexto para la plantilla
    context = {
        'reservaciones': reservaciones,
        'myFilter': myFilter,
        'salas': salas,
        'areas': areas,  # Necesario para mostrar opciones en el modal de gestión de invitados
    }

    return render(request, 'administracion.html', context)


