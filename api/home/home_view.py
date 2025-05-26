from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib import messages
from api.models import SalaJuntas, Reservacion,Area,Invitado,ReservacionInvitado
from django.http import JsonResponse
from datetime import datetime
import json
from api.filters import ReservacionFilter
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail

@login_required (login_url= 'login')
def Home(request):
    if request.user.is_superuser:
        template_view = "home-user.html"
        return render(request, template_name=template_view)
    else:
        return redirect("homeuser")

@login_required
def HomeUser(request):
    if request.method == 'POST':
        nueva_contrasena = request.POST.get('nuevaContrasena')
        confirmar_contrasena = request.POST.get('confirmarContrasena')

        # Verificar si las contraseñas coinciden
        if nueva_contrasena != confirmar_contrasena:
            # Mensaje de error que se mostrará en el modal
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'home-user.html')  # Mantener el modal abierto

        # Si las contraseñas coinciden, cambiar la contraseña del usuario
        user = request.user
        user.set_password(nueva_contrasena)
        user.save()

        # Actualizar la sesión para que no se cierre después de cambiar la contraseña
        update_session_auth_hash(request, user)

        # Cerrar sesión del usuario
        logout(request)

        # Mensaje de éxito y redirigir al login
        messages.success(request, "Contraseña cambiada exitosamente. Por favor, vuelve a iniciar sesión.")
        return redirect('login')  # Redirige al login después de cerrar sesión

    # Si no es un POST, solo se muestra el formulario
    return render(request, 'home-user.html')


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
                    message = (
                        f"La reservación para '{evento}' ha sido realizada.\n"
                        f"📍 *Sala:* {sala}\n"  # Agregar la sala de reservación
                        f"📅 *Fecha:* {fecha_reservacion}\n"
                        f"⏰ *Horario:* {hora_inicio} - {hora_final}"
                    )
                    send_mail(subject, message, 'noreply@miapp.com', destinatarios_correo)

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