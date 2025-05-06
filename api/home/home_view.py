from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib import messages
from api.models import SalaJuntas, Reservacion
from django.http import JsonResponse
from datetime import datetime
import json
from api.filters import ReservacionFilter

@login_required (login_url= 'login')
def Home(request):
    if request.user.is_superuser:
        template_view = "home.html"
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
    myFilter = ReservacionFilter(request.GET, queryset=reservaciones)
    reservaciones = myFilter.qs
    salas = SalaJuntas.objects.all()

    if request.method == 'POST':
        # Obtener los datos del formulario
        fecha_reservacion = request.POST.get('fechaReservacion')
        hora_inicio_str = request.POST.get('horaInicio')
        hora_final_str = request.POST.get('horaFinal')
        sala_id = request.POST.get('salaJuntas')
        evento = request.POST.get('evento')
        comentarios = request.POST.get('comentarios', '')

        try:
            hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
            hora_final = datetime.strptime(hora_final_str, '%H:%M').time()
        except ValueError:
            # Esta validación ya se realiza en el lado del cliente
            pass

        sala = SalaJuntas.objects.get(id_sala=sala_id)

        # Guardar la nueva reservación
        Reservacion.objects.create(
            evento=evento,
            comentarios=comentarios,
            fecha=fecha_reservacion,
            hora_inicio=hora_inicio,
            hora_final=hora_final,
            sala=sala,
            usuario=request.user  # Agregar el usuario que hace la reservación
        )

        messages.success(request, f"Reservación realizada con éxito para '{evento}'.")
        return redirect('reservation')

    return render(request, "reservation.html", {'salas': salas, 'reservaciones': reservaciones, 'myFilter': myFilter})
    
def get_ocupados(request):
    sala_id = request.GET.get('sala_id')
    fecha = request.GET.get('fecha')

    ocupados = Reservacion.objects.filter(sala_id=sala_id, fecha=fecha).values('hora_inicio', 'hora_final')

    return JsonResponse(list(ocupados), safe=False)

def mostrar_reservaciones(request):
    reservaciones = Reservacion.objects.filter(usuario=request.user)
    return render(request, 'reservaciones.html', {'reservaciones': reservaciones})