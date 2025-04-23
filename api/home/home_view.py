from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from api.models import Reservacion, SalaJuntas


@login_required (login_url= 'login')
def Home(request):
    if request.user.is_superuser:
        template_view = "home.html"
        return render(request, template_name=template_view)
    else:
        return redirect("homeuser")
    


@login_required
def HomeUser(request):
    template_view = "home-user.html"

    # Obtener las salas de juntas
    salas = SalaJuntas.objects.all()

    # Procesar la creación de la reservación
    if request.method == 'POST':
        evento = request.POST.get('evento')
        comentarios = request.POST.get('comentarios')
        fecha = request.POST.get('fechaReservacion')
        hora_inicio = request.POST.get('horaInicio')
        hora_fin = request.POST.get('horaFin')
        sala_id = request.POST.get('salaJuntas')
        num_personas = request.POST.get('numPersonas')
        
        # Validación de campos requeridos
        if not evento or not fecha or not hora_inicio or not hora_fin or not sala_id or not num_personas:
            messages.error(request, "Por favor, complete todos los campos.")
            return redirect('homeuser')

        try:
            # Obtener la sala seleccionada
            sala = SalaJuntas.objects.get(id_sala=sala_id)

            # Crear la nueva reservación
            nueva_reservacion = Reservacion.objects.create(
                evento=evento,
                comentarios=comentarios,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_final=hora_fin,
                sala=sala
            )

            # Mostrar un mensaje de éxito
            messages.success(request, "¡Reservación creada con éxito!")

        except SalaJuntas.DoesNotExist:
            messages.error(request, "La sala seleccionada no existe.")

        return redirect('homeuser')  # Redirige a la página de inicio después de la reservación

    # Pasar las salas al contexto
    context = {
        'salas': salas,
    }

    return render(request, template_name=template_view, context=context)