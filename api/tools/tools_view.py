from django.shortcuts import render, redirect
from django.db.models import Count
from django.contrib.auth.models import User
from api.models import Reservacion, SalaJuntas,Invitado,Area
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
from django.core.mail import send_mail
from datetime import date, timedelta
from collections import defaultdict
from django.contrib import messages


def graficos(request):
    mes = request.GET.get('mes')
    semana = request.GET.get('semana')
    ano = request.GET.get('ano')

    reservaciones = Reservacion.objects.all()
    filtros_seleccionados = False

    if mes and ano:
        if semana:
            # Filtro por semana
            first_day = date(int(ano), int(mes), 1)
            first_day_weekday = first_day.weekday()
            days_offset = (int(semana) - 1) * 7 - first_day_weekday
            if days_offset < 0:
                days_offset = 0
            start_date = first_day + timedelta(days=days_offset)
            end_date = start_date + timedelta(days=6)
            reservaciones = reservaciones.filter(fecha__range=[start_date, end_date])
        else:
            # Filtro por mes
            reservaciones = reservaciones.filter(fecha__month=mes, fecha__year=ano)
        filtros_seleccionados = True

    context = {
        'anos': range(2025, datetime.now().year + 5),
    }

    if filtros_seleccionados:
        # --- Gráfico 1: Reservaciones por usuario ---
        reservaciones_por_usuario = reservaciones.values('usuario__username').annotate(total_reservaciones=Count('id_reservacion')).order_by('-total_reservaciones')
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

        # --- Gráfico 2: Reservaciones por sala de juntas (en total) ---
        reservaciones_por_sala = reservaciones.values('sala__nombre').annotate(total_reservaciones=Count('id_reservacion')).order_by('-total_reservaciones')
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
            reservas_sala = reservaciones.filter(sala=sala).values('usuario__username').annotate(total_reservaciones=Count('id_reservacion')).order_by('-total_reservaciones')
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

        context['imagen_usuario'] = imagen_usuario_base64
        context['imagen_sala_total'] = imagen_sala_total_base64
        context['graficos_por_sala'] = graficos_por_sala

    return render(request, 'graficos.html', context)

#Buenoooo
def editar_reservacion(request, pk):
    if request.method == 'POST':
        try:
            reservacion = get_object_or_404(Reservacion, id_reservacion=pk)

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
    if not reservacion_id or not reservacion_id.isdigit():  
        return JsonResponse({'error': 'ID de reservación no válido'}, status=400)

    reservacion_id = int(reservacion_id)  
    reservacion = get_object_or_404(Reservacion, id_reservacion=reservacion_id)

    invitados_actuales_ids = list(map(int, reservacion.reservacioninvitado_set.values_list('invitado_id', flat=True)))

    invitados_actuales = list(Invitado.objects.filter(id_invitado__in=invitados_actuales_ids).values('id_invitado', 'nombre_completo'))
    invitados_disponibles = list(Invitado.objects.exclude(id_invitado__in=invitados_actuales_ids).values('id_invitado', 'nombre_completo'))

    areas = Area.objects.prefetch_related('invitados').all()
    areas_data = []
    for area in areas:
        area_data = {
            'id_area': area.id_area,
            'nombre': area.nombre,
            'invitados': list(area.invitados.values('id_invitado', 'nombre_completo'))
        }
        areas_data.append(area_data)

    return JsonResponse({
        'invitados_actuales': invitados_actuales, 
        'invitados_disponibles': invitados_disponibles,
        'areas': areas_data
    })


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
    
def obtener_semanas_reservaciones():
    hoy = date.today()
    reservas = Reservacion.objects.filter(fecha__gte=hoy).order_by('fecha', 'hora_inicio')

    # Agrupar por semana (año, número de semana)
    semanas = defaultdict(list)
    for reserva in reservas:
        anio, semana, _ = reserva.fecha.isocalendar()
        semanas[(anio, semana)].append(reserva)

    return semanas

def vista_reservas_semanales(request):
    semanas_reservas = obtener_semanas_reservaciones()

    # Construir datos para el template
    datos = []
    for (anio, semana), reservas in semanas_reservas.items():
        primer_dia_semana = date.fromisocalendar(anio, semana, 1)
        ultimo_dia_semana = primer_dia_semana + timedelta(days=6)
        datos.append({
            'rango': f"Semana del {primer_dia_semana.strftime('%d %b')} al {ultimo_dia_semana.strftime('%d %b')}",
            'reservas': reservas
        })

    datos.sort(key=lambda x: x['rango'])  # Ordenar cronológicamente

    return render(request, 'reservas_semanales.html', {'datos': datos})

def enviar_notificacion(request):
    if request.method == 'POST':
        mensaje = request.POST.get('mensaje')
        destinatarios = request.POST.get('destinatarios')
        destinatarios = destinatarios.split(',')

        invitados = Invitado.objects.filter(id_invitado__in=destinatarios)

        for invitado in invitados:
            send_mail(
                'Notificación',
                mensaje,
                'informatica.cdt.stc@gmail.com',
                [invitado.correo],
                fail_silently=False,
            )

        return redirect('home')  

    areas = Area.objects.all()  
    return render(request, 'enviar_notificacion.html', {'areas': areas})



def eliminar_reservacion(request, pk):
    reservacion = get_object_or_404(Reservacion, id_reservacion=pk)
    motivo = request.POST.get('motivo')
    
    # Enviar correo a admin con motivo
    subject_admin = f"Reservación eliminada: {reservacion.evento}"
    message_admin = f"""
        <h2>Reservación eliminada</h2>
        <p>La reservación para {reservacion.evento} ha sido eliminada.</p>
        <p>Fecha: {reservacion.fecha}</p>
        <p>Hora de inicio: {reservacion.hora_inicio}</p>
        <p>Hora de fin: {reservacion.hora_final}</p>
        <p>Motivo de eliminación: {motivo}</p>
    """
    send_mail(subject_admin, "", 'informatica.cdt.stc@gmail.com', ['eliasaranda055@gmail.com'], html_message=message_admin)
    
    # Enviar correo a invitados
    invitados = Invitado.objects.filter(reservacioninvitado__reservacion=reservacion)
    for invitado in invitados:
        subject = f"Reservación eliminada: {reservacion.evento}"
        message = f"""
            <h2>Reservación eliminada</h2>
            <p>La reservación para {reservacion.evento} ha sido eliminada.</p>
            <p>Fecha: {reservacion.fecha}</p>
            <p>Hora de inicio: {reservacion.hora_inicio}</p>
            <p>Hora de fin: {reservacion.hora_final}</p>
        """
        send_mail(subject, "", 'informatica.cdt.stc@gmail.com', [invitado.correo], html_message=message)
    
    reservacion.delete()
    return JsonResponse({'success': True})