from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from api.models import SalaJuntas, Reservacion,Area,Invitado,ReservacionInvitado
from django.http import JsonResponse
from datetime import datetime
import json
from api.filters import ReservacionFilter
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse

@login_required (login_url= 'login')
def Home(request):
    if request.user.is_superuser:
        template_view = "home.html"
        return render(request, template_name=template_view)
    else:
        return redirect("homeuser")


@login_required
def Reservation(request):
    reservaciones = Reservacion.objects.filter(usuario=request.user)
    areas = Area.objects.prefetch_related('invitados').all()  # Cargar áreas y sus invitados
    salas = SalaJuntas.objects.all()

    fecha = request.GET.get('fecha')
    if fecha == 'actuales_y_futuras':
        reservaciones = reservaciones.filter(fecha__gte=timezone.now().date())

    # Aplicar filtro a las reservaciones
    myFilter = ReservacionFilter(request.GET, queryset=reservaciones)
    reservaciones = myFilter.qs

    # Determinar si una reservación es editable
    for reservacion in reservaciones:
        hora_inicio = datetime.combine(reservacion.fecha, reservacion.hora_inicio)
        reservacion.editable = hora_inicio - datetime.now() >= timedelta(hours=1)

    if request.method == 'POST':
        # Obtener datos del formulario
        fecha_reservacion = request.POST.get('fechaReservacion')
        hora_inicio_str = request.POST.get('horaInicio')
        hora_final_str = request.POST.get('horaFinal')
        sala_id = request.POST.get('salaJuntas')
        evento = request.POST.get('evento')
        comentarios = request.POST.get('comentarios', '')
        enviar_correo = request.POST.get('notificarReserva') == "on"
        destinatarios_ids = request.POST.get('destinatariosSeleccionados', "")

        # Validar que los destinatarios se están recibiendo correctamente
        print(f"Destinatarios recibidos en la solicitud: {destinatarios_ids}")  # Depuración en consola

        destinatarios_ids = destinatarios_ids.split(",") if destinatarios_ids else []  # Convertir en lista

        try:
            # Convertir fecha y hora al formato correcto
            fecha_reservacion = datetime.strptime(fecha_reservacion, '%Y-%m-%d').date()
            hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
            hora_final = datetime.strptime(hora_final_str, '%H:%M').time()
        except ValueError:
            messages.error(request, "Fecha o hora inválida. Asegúrate de usar el formato correcto.")
            return redirect('reservation')

        sala = SalaJuntas.objects.get(id_sala=sala_id)

        # Guardar la nueva reservación
        nueva_reservacion = Reservacion.objects.create(
            evento=evento,
            comentarios=comentarios,
            fecha=fecha_reservacion,
            hora_inicio=hora_inicio,
            hora_final=hora_final,
            sala=sala,
            usuario=request.user,
            enviar_correo=enviar_correo
        )

        # Guardar múltiples destinatarios solo si hay datos válidos
        if destinatarios_ids and destinatarios_ids[0] != "":
            invitados_a_guardar = [
                ReservacionInvitado(reservacion=nueva_reservacion, invitado=Invitado.objects.get(id_invitado=int(destinatario_id)))
                for destinatario_id in destinatarios_ids if destinatario_id.strip().isdigit()
            ]
            
            # Inserción masiva en la base de datos
            ReservacionInvitado.objects.bulk_create(invitados_a_guardar)

        # Enviar correos si la opción de notificación está activada
        if enviar_correo and destinatarios_ids:
            destinatarios_correo = [invitado.correo for invitado in Invitado.objects.filter(id_invitado__in=destinatarios_ids)]
            if destinatarios_correo:
                subject = f"Confirmación de Reservación: {evento}"
                reservas_url = request.build_absolute_uri(reverse('reservas_semanales'))
                for invitado in Invitado.objects.filter(id_invitado__in=destinatarios_ids):
                    message = f"""
                        <h2>📅 Confirmación de Reservación</h2>
                        <p>Estimado/a {invitado.nombre_completo},</p>
                        <p>La reservación para <strong>{evento}</strong> ha sido realizada por {request.user.username}.</p>
                        <h3>Detalles de la Reservación:</h3>
                        <ul>
                            <li>📆 Fecha: {fecha_reservacion}</li>
                            <li>🕒 Hora de inicio: {hora_inicio}</li>
                            <li>🕒 Hora de finalización: {hora_final}</li>
                            <li>🏢 Sala: {sala}</li>
                        </ul>
                        <p>Puedes checar las reservaciones para esta semana en este enlace: <a href="{reservas_url}">Reservas semanales</a></p>
                        <p>Atentamente,</p>
                        <p>{request.user.username}</p>
                    """
                    send_mail(subject, "", 'noreply@miapp.com', [invitado.correo], html_message=message)

                messages.success(request, f"Reservación realizada con éxito para '{evento}'.")


        return redirect('reservation')

    return render(request, "reservation.html", {
        'salas': salas,
        'reservaciones': reservaciones,
        'areas': areas,  # Se envían las áreas al template
        'myFilter': myFilter,
        'today': timezone.now().date()
    })


def get_ocupados(request):
    try:
        sala_id = request.GET.get('sala_id')
        fecha = request.GET.get('fecha')
        reservacion_id = request.GET.get('reservacion_id')
        if reservacion_id:
            ocupados = Reservacion.objects.filter(sala_id=sala_id, fecha=fecha).exclude(id_reservacion=reservacion_id).values('hora_inicio', 'hora_final')
        else:
            ocupados = Reservacion.objects.filter(sala_id=sala_id, fecha=fecha).values('hora_inicio', 'hora_final')
        return JsonResponse(list(ocupados), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def Notificaciones(request):
    areas = Area.objects.all()
    if request.method == 'POST':
        destinatarios = request.POST.get('destinatarios')
        mensaje = request.POST.get('mensaje')
        # Procesa los datos y envía el correo electrónico
        destinatarios = destinatarios.split(',')
        # Obtiene los correos electrónicos de los destinatarios
        correos = [Invitado.objects.get(id_invitado=destinatario).correo for destinatario in destinatarios]
        # Envía el correo electrónico
        send_mail('Notificación', mensaje, 'informatica.cdt.stc@gmail.com', correos)
    return render(request, 'notificaciones.html', {'areas': areas})
