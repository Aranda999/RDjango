from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.models import User
from api.models import Reservacion, SalaJuntas,Invitado
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import pandas as pd
from datetime import timedelta
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from api.models import Reservacion, Invitado, ReservacionInvitado


def graficos(request):
    # --- Gráfico 1: Reservaciones por usuario ---
    reservaciones_por_usuario = Reservacion.objects.values('usuario__username').annotate(total_reservaciones=Count('id_reservacion')).order_by('-total_reservaciones')
    usuarios = [item['usuario__username'] for item in reservaciones_por_usuario]
    cantidad_reservaciones_usuario = [item['total_reservaciones'] for item in reservaciones_por_usuario]

    df = pd.DataFrame({'usuario': usuarios, 'cantidad': cantidad_reservaciones_usuario})
    plt.figure(figsize=(10, 6))
    colors = sns.color_palette("viridis", len(df))
    sns.barplot(x='usuario', y='cantidad', data=df, palette=colors)
    plt.xlabel("Usuario", fontsize=16)
    plt.ylabel("Número de Reservaciones", fontsize=16)
    plt.title("Total de Reservaciones por Usuario", fontsize=18)
    plt.xticks(rotation=45, ha="right", fontsize=14)
    plt.yticks(fontsize=14)
    plt.tight_layout()
    buffer_usuario = io.BytesIO()
    plt.savefig(buffer_usuario, format='png')
    buffer_usuario.seek(0)
    imagen_usuario_base64 = base64.b64encode(buffer_usuario.read()).decode('utf-8')
    plt.close()

    # --- Gráfico 2: Reservaciones por sala de juntas (total) ---
    reservaciones_por_sala = Reservacion.objects.values('sala__nombre').annotate(total_reservaciones=Count('id_reservacion')).order_by('-total_reservaciones')
    salas = [item['sala__nombre'] for item in reservaciones_por_sala]
    cantidad_reservaciones_sala = [item['total_reservaciones'] for item in reservaciones_por_sala]

    plt.figure(figsize=(8, 8))
    plt.pie(cantidad_reservaciones_sala, labels=salas, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"), textprops={'fontsize': 20})
    plt.title("Reservaciones por Sala de Juntas (Total)", fontsize=20)
    plt.tight_layout()
    buffer_sala_total = io.BytesIO()
    plt.savefig(buffer_sala_total, format='png')
    buffer_sala_total.seek(0)
    imagen_sala_total_base64 = base64.b64encode(buffer_sala_total.read()).decode('utf-8')
    plt.close()

    # --- Gráfico 3: Reservaciones por sala de juntas (separado) ---
    graficos_por_sala = {}
    salas_juntas = SalaJuntas.objects.all()
    for sala in salas_juntas:
        reservas_sala = Reservacion.objects.filter(sala=sala).values('usuario__username').annotate(total_reservaciones=Count('id_reservacion')).order_by('-total_reservaciones')
        usuarios_sala = [item['usuario__username'] for item in reservas_sala]
        cantidad_reservaciones_sala_usuario = [item['total_reservaciones'] for item in reservas_sala]

        df_sala = pd.DataFrame({'usuario': usuarios_sala, 'cantidad': cantidad_reservaciones_sala_usuario})
        plt.figure(figsize=(11, 8))
        colors = sns.color_palette("mako", len(df_sala))
        sns.barplot(x='usuario', y='cantidad', data=df_sala, palette=colors)
        plt.xlabel("Usuario", fontsize=20)
        plt.ylabel(f"Reservaciones en {sala.nombre}", fontsize=18)
        plt.title(f"Reservaciones por el Usuario en Sala: {sala.nombre}", fontsize=20)
        plt.xticks(rotation=45, ha="right", fontsize=22)
        plt.yticks(fontsize=20)
        plt.tight_layout()
        buffer_sala_individual = io.BytesIO()
        plt.savefig(buffer_sala_individual, format='png')
        buffer_sala_individual.seek(0)
        imagen_sala_individual_base64 = base64.b64encode(buffer_sala_individual.read()).decode('utf-8')
        plt.close()
        graficos_por_sala[sala.nombre] = imagen_sala_individual_base64

    context = {
        'imagen_usuario': imagen_usuario_base64,
        'imagen_sala_total': imagen_sala_total_base64,
        'graficos_por_sala': graficos_por_sala,
        'salas_juntas': salas_juntas,
    }
    return render(request, 'graficos.html', context)


# bueno
def editar_reservacion(request, pk):
    if request.method == 'POST':
        try:
            reservacion = get_object_or_404(Reservacion, id_reservacion=pk)

            # Obtener datos enviados y conservar los originales si están vacíos
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
                invitados_seleccionados = request.POST.get('invitados').strip('[]').split(',')
                invitados_seleccionados = [int(i) for i in invitados_seleccionados if i]
            
            ReservacionInvitado.objects.filter(reservacion=reservacion).delete()
            for invitado_id in invitados_seleccionados:
                ReservacionInvitado.objects.create(reservacion=reservacion, invitado_id=invitado_id)

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

def get_destinatarios_por_area(request):
    try:
        area_id = request.GET.get('area_id')
        if not area_id:
            return JsonResponse({'error': 'Área no especificada'}, status=400)
        
        invitados = Invitado.objects.filter(id_area=area_id).values('id_invitado', 'nombre_completo', 'correo')
        return JsonResponse(list(invitados), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_invitados(request):
    reservacion_id = request.GET.get('reservacion_id')
    if not reservacion_id or not reservacion_id.isdigit():  # Validación extra
        return JsonResponse({'error': 'ID de reservación no válido'}, status=400)

    reservacion_id = int(reservacion_id)  # Convertir a entero correctamente
    reservacion = get_object_or_404(Reservacion, id_reservacion=reservacion_id)

    invitados_actuales_ids = list(map(int, reservacion.reservacioninvitado_set.values_list('invitado_id', flat=True)))

    invitados_actuales = list(Invitado.objects.filter(id_invitado__in=invitados_actuales_ids).values('id_invitado', 'nombre_completo'))
    invitados_disponibles = list(Invitado.objects.exclude(id_invitado__in=invitados_actuales_ids).values('id_invitado', 'nombre_completo'))

    return JsonResponse({'invitados_actuales': invitados_actuales, 'invitados_disponibles': invitados_disponibles})



@csrf_exempt
def guardar_invitados(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        reservacion_id = data.get('reservacion_id')
        invitados_ids = data.get('invitados', [])

        reservacion = get_object_or_404(Reservacion, id_reservacion=reservacion_id)
        invitados_actuales_ids = list(reservacion.reservacioninvitado_set.values_list('invitado_id', flat=True))

        # Determinar invitados nuevos y eliminados
        invitados_a_agregar = set(invitados_ids) - set(invitados_actuales_ids)
        invitados_a_eliminar = set(invitados_actuales_ids) - set(invitados_ids)

        # Agregar nuevos invitados
        nuevos_invitados = [
            ReservacionInvitado(reservacion=reservacion, invitado=Invitado.objects.get(id_invitado=invitado_id))
            for invitado_id in invitados_a_agregar
        ]
        if nuevos_invitados:
            ReservacionInvitado.objects.bulk_create(nuevos_invitados)

        # Eliminar invitados removidos
        if invitados_a_eliminar:
            ReservacionInvitado.objects.filter(reservacion=reservacion, invitado_id__in=invitados_a_eliminar).delete()

        return JsonResponse({'success': True, 'message': 'Invitados actualizados correctamente'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)