from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.models import User
from api.models import Reservacion, SalaJuntas
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
    plt.title("Porcentaje de Reservaciones por Sala de Juntas (Total)", fontsize=20)
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
            reservacion = Reservacion.objects.get(id_reservacion=pk)
        except Reservacion.DoesNotExist:
            return JsonResponse({'success': False}, status=404)

        reservacion.evento = request.POST.get('evento_editar')
        reservacion.comentarios = request.POST.get('comentarios_editar')
        reservacion.sala_id = request.POST.get('salaJuntas_editar')
        reservacion.fecha = request.POST.get('fechaReservacion_editar')
        reservacion.hora_inicio = request.POST.get('horaInicio_editar')
        reservacion.hora_final = request.POST.get('horaFinal_editar')
        reservacion.save()

        return JsonResponse({'success': True})

    elif request.method == 'GET':
        try:
            reservacion = Reservacion.objects.get(id_reservacion=pk)
        except Reservacion.DoesNotExist:
            return JsonResponse({'success': False}, status=404)

        data = {
            'evento': reservacion.evento,
            'comentarios': reservacion.comentarios,
            'sala_id': reservacion.sala_id,
            'fecha': reservacion.fecha,
            'hora_inicio': reservacion.hora_inicio,
            'hora_final': reservacion.hora_final,
        }

        return JsonResponse(data)