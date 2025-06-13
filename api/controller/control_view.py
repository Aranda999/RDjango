from django.shortcuts import get_object_or_404, render,redirect
from api.models import Reservacion, ReservacionInvitado, SalaJuntas,Invitado
from api.filters import ReservacionFilter  
from datetime import datetime, timedelta, date
from django.core.mail import send_mail




def administracion(request):
    salas = SalaJuntas.objects.all()
    filtro_fecha = request.GET.get('fecha')
    reservaciones = Reservacion.objects.all().order_by('fecha', 'hora_inicio')

    if filtro_fecha == 'actuales_y_futuras':
        reservaciones = reservaciones.filter(fecha__gte=date.today())

    # Aplicar filtro
    myFilter = ReservacionFilter(request.GET, queryset=reservaciones)  
    reservaciones = myFilter.qs  


    # Agregar lógica para determinar si puede editarse o eliminarse
    ahora = datetime.now()
    for reservacion in reservaciones:
        inicio_reservacion = datetime.combine(reservacion.fecha, reservacion.hora_inicio)
        reservacion.editable = inicio_reservacion > ahora + timedelta(hours=1)
        reservacion.eliminable = inicio_reservacion > ahora + timedelta(hours=1)

    if request.method == 'POST':
        if 'eliminar_reservacion' in request.POST:
            # Código existente para eliminar reservaciones
            id_reservacion = request.POST.get('id_reservacion')
            reservacion = Reservacion.objects.get(id_reservacion=id_reservacion)
            # Enviar correo con mensaje de eliminación
            subject = f"Reservación eliminada: {reservacion.evento}"
            message = f"""
                <h2>Reservación eliminada</h2>
                <p>La reservación para {reservacion.evento} ha sido eliminada.</p>
                <p>Fecha: {reservacion.fecha}</p>
                <p>Hora de inicio: {reservacion.hora_inicio}</p>
                <p>Hora de fin: {reservacion.hora_final}</p>
            """
            send_mail(subject, "", 'informatica.cdt.stc@gmail.com', ['eliasaranda055@gmail.com'], html_message=message)
            
            reservacion.delete()
            return redirect('administracion')
        elif 'editar_reservacion' in request.POST:
            id_reservacion = request.POST.get('id_reservacion')
            reservacion = get_object_or_404(Reservacion, id_reservacion=id_reservacion)

            # Obtener datos enviados y conservar los originales si están vacíos
            nombre_anterior = reservacion.evento
            reservacion.evento = request.POST.get('evento_editar', reservacion.evento)
            reservacion.comentarios = request.POST.get('comentarios_editar', reservacion.comentarios)
            reservacion.sala_id = request.POST.get('salaJuntas_editar', reservacion.sala_id)
            reservacion.fecha = request.POST.get('fechaReservacion_editar') or reservacion.fecha
            reservacion.hora_inicio = request.POST.get('horaInicio_editar') or reservacion.hora_inicio
            reservacion.hora_final = request.POST.get('horaFinal_editar') or reservacion.hora_final
            
            reservacion.save()

            # Procesar invitados seleccionados
            invitados_seleccionados = request.POST.getlist('invitados[]')
            if not invitados_seleccionados:
                invitados_seleccionados = request.POST.get('invitados')
                if invitados_seleccionados:
                    invitados_seleccionados = invitados_seleccionados.strip('[]').split(',')
                    invitados_seleccionados = [int(i) for i in invitados_seleccionados if i]
                else:
                    invitados_seleccionados = []

            ReservacionInvitado.objects.filter(reservacion=reservacion).delete()
            if invitados_seleccionados:
                for invitado_id in invitados_seleccionados:
                    ReservacionInvitado.objects.create(reservacion=reservacion, invitado_id=invitado_id)

            # Enviar correo electrónico a los invitados
            if invitados_seleccionados:
                invitados = Invitado.objects.filter(id_invitado__in=invitados_seleccionados)
                for invitado in invitados:
                    subject = f"Actualización de Reservación: {reservacion.evento}"
                    if nombre_anterior != reservacion.evento:
                        message = f"""
                            <h2>📅 Actualización de Reservación</h2>
                            <p>Estimado/a {invitado.nombre_completo},</p>
                            <p>La reservación <strong>{nombre_anterior}</strong> ha sido actualizada a <strong>{reservacion.evento}</strong> por {reservacion.usuario.username}.</p>
                            <h3>Detalles de la Reservación:</h3>
                            <ul>
                                <li>📆 Fecha: {reservacion.fecha}</li>
                                <li>🕒 Hora de inicio: {reservacion.hora_inicio}</li>
                                <li>🕒 Hora de finalización: {reservacion.hora_final}</li>
                                <li>🏢 Sala: {reservacion.sala.nombre}</li>
                            </ul>
                            <p>Por favor, revise los detalles y confirme su asistencia.</p>
                            <p>Atentamente,</p>
                            <p>{reservacion.usuario.username}</p>
                        """
                    else:
                        message = f"""
                            <h2>📅 Actualización de Reservación</h2>
                            <p>Estimado/a {invitado.nombre_completo},</p>
                            <p>La reservación para <strong>{reservacion.evento}</strong> ha sido actualizada por {reservacion.usuario.username}.</p>
                            <h3>Detalles de la Reservación:</h3>
                            <ul>
                                <li>📆 Fecha: {reservacion.fecha}</li>
                                <li>🕒 Hora de inicio: {reservacion.hora_inicio}</li>
                                <li>🕒 Hora de finalización: {reservacion.hora_final}</li>
                                <li>🏢 Sala: {reservacion.sala.nombre}</li>
                            </ul>
                            <p>Por favor, revise los detalles y confirme su asistencia.</p>
                            <p>Atentamente,</p>
                            <p>{reservacion.usuario.username}</p>
                        """
                    send_mail(subject, "", 'informatica.cdt.stc@gmail.com', [invitado.correo], html_message=message)

            return redirect('administracion')

    context = {
        'reservaciones': reservaciones,
        'myFilter': myFilter,
        'salas': salas
    }

    return render(request, 'administracion.html', context)
