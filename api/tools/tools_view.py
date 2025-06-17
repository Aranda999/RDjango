from django.shortcuts import render, redirect
from django.db.models import Count
from django.contrib.auth.models import User
from api.models import Reservacion, SalaJuntas,Invitado,Area
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
from django.urls import reverse
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
from django.db.models import Count
from django.http import HttpResponse 
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Tu función graficos existente
def graficos(request):
    mes = request.GET.get('mes')
    semana = request.GET.get('semana')
    ano = request.GET.get('ano')

    reservaciones = Reservacion.objects.all()
    filtros_seleccionados = False

    if mes and ano:
        if semana:
            # Filtro por semana (tu lógica existente)
            first_day = date(int(ano), int(mes), 1)
            first_day_weekday = first_day.weekday() 
            first_monday_of_month_week = first_day - timedelta(days=first_day.weekday())

            start_date = first_monday_of_month_week + timedelta(days=(int(semana) - 1) * 7)
            end_date = start_date + timedelta(days=6)

            reservaciones = reservaciones.filter(fecha__range=[start_date, end_date])
        else:
            # Filtro por mes (tu lógica existente)
            reservaciones = reservaciones.filter(fecha__month=mes, fecha__year=ano)
        filtros_seleccionados = True

    context = {
        'anos': range(datetime.now().year , datetime.now().year + 5), # Rango de años más dinámico
        'imagen_usuario': None,
        'imagen_sala_total': None,
        'graficos_por_sala': None,
    }

    if filtros_seleccionados:
        # --- Generación de gráficos (tu código existente, asegúrate de que se ejecute si hay datos) ---
        
        # Gráfico 1: Reservaciones por usuario
        reservaciones_por_usuario = reservaciones.values('usuario__username').annotate(total_reservaciones=Count('id_reservacion')).order_by('-total_reservaciones')
        if reservaciones_por_usuario: # Solo genera si hay datos
            usuarios = [item['usuario__username'] for item in reservaciones_por_usuario]
            cantidad_reservaciones_usuario = [item['total_reservaciones'] for item in reservaciones_por_usuario]
            df = pd.DataFrame({'usuario': usuarios, 'cantidad': cantidad_reservaciones_usuario})
            
            plt.figure(figsize=(11, 7))
            colors = sns.color_palette("viridis", len(df))
            sns.barplot(x='usuario', y='cantidad', data=df, palette=colors)
            plt.xlabel("Usuario", fontsize=18)
            plt.ylabel("Número de Reservaciones", fontsize=16)
            plt.title("Total de Reservaciones por Usuario", fontsize=18)
            plt.xticks(rotation=45, ha="right", fontsize=20)
            plt.yticks(fontsize=18)
            plt.tight_layout()
            buffer_usuario = io.BytesIO()
            plt.savefig(buffer_usuario, format='png')
            buffer_usuario.seek(0)
            context['imagen_usuario'] = base64.b64encode(buffer_usuario.read()).decode('utf-8')
            plt.close()

        # Gráfico 2: Reservaciones por sala de juntas (en total)
        reservaciones_por_sala_total = reservaciones.values('sala__nombre').annotate(total_reservaciones=Count('id_reservacion')).order_by('-total_reservaciones')
        if reservaciones_por_sala_total:  # Solo genera si hay datos
            salas = [item['sala__nombre'] for item in reservaciones_por_sala_total]
            cantidad_reservaciones_sala = [item['total_reservaciones'] for item in reservaciones_por_sala_total]
            
            df = pd.DataFrame({
                'sala': salas,
                'reservaciones': cantidad_reservaciones_sala
            })

            plt.figure(figsize=(12, 8))
            sns.barplot(x='sala', y='reservaciones', data=df, palette='crest', hue='sala', legend=False)
            plt.title("Reservaciones por Sala de Juntas (Total)", fontsize=23)
            plt.xlabel("Sala",fontsize=20 )
            plt.ylabel("Reservaciones", fontsize=21)
            plt.xticks(rotation=45, fontsize=20)
            plt.tight_layout()

            buffer_sala_total = io.BytesIO()
            plt.savefig(buffer_sala_total, format='png')
            buffer_sala_total.seek(0)
            context['imagen_sala_total'] = base64.b64encode(buffer_sala_total.read()).decode('utf-8')
            plt.close()

        # Gráfico 3: Reservaciones por sala de juntas (separado)
        graficos_por_sala_dict = {}
        salas_juntas = SalaJuntas.objects.all()
        for sala in salas_juntas:
            reservas_sala = reservaciones.filter(sala=sala).values('usuario__username').annotate(total_reservaciones=Count('id_reservacion')).order_by('-total_reservaciones')
            if reservas_sala: # Solo genera si hay datos para esta sala
                usuarios_sala = [item['usuario__username'] for item in reservas_sala]
                cantidad_reservaciones_sala_usuario = [item['total_reservaciones'] for item in reservas_sala]
                df_sala = pd.DataFrame({'usuario': usuarios_sala, 'cantidad': cantidad_reservaciones_sala_usuario})
                
                plt.figure(figsize=(11, 8))
                colors = sns.color_palette("mako", len(df_sala))
                sns.barplot(x='usuario', y='cantidad', data=df_sala, palette=colors)
                plt.xlabel("Usuario", fontsize=20)
                plt.ylabel(f"Reservaciones en {sala.nombre}", fontsize=22)
                plt.title(f"Reservaciones por el Usuario en Sala: {sala.nombre}", fontsize=22)
                plt.xticks(rotation=45, ha="right", fontsize=22)
                plt.yticks(fontsize=(20))
                plt.tight_layout()
                buffer_sala_individual = io.BytesIO()
                plt.savefig(buffer_sala_individual, format='png')
                buffer_sala_individual.seek(0)
                imagen_sala_individual_base64 = base64.b64encode(buffer_sala_individual.read()).decode('utf-8')
                plt.close()
                graficos_por_sala_dict[sala.nombre] = imagen_sala_individual_base64
        
        if graficos_por_sala_dict: # Solo agrega al contexto si hay gráficos generados
            context['graficos_por_sala'] = graficos_por_sala_dict

    return render(request, 'graficos.html', context)


from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from copy import deepcopy
import os
from django.conf import settings


from textwrap import wrap

def generar_pagina_resumen(base_page, titulo, resumen_texto):
    temp = BytesIO()
    can = canvas.Canvas(temp, pagesize=letter)

    # 🏷️ Título en la parte superior
    can.setFont("Helvetica-Bold", 16)
    can.drawCentredString(300, 695, titulo)  # Ubicación del título (más arriba de lo que estaba antes)

    # 📝 Resumen debajo del título
    text = can.beginText()
    text.setTextOrigin(70, 672)  # Más cerca del título
    text.setFont("Helvetica", 12)
    for linea in wrap(resumen_texto, width=95):
        text.textLine(linea)

    can.drawText(text)
    can.save()
    texto = PdfReader(BytesIO(temp.getvalue())).pages[0]
    hoja = deepcopy(base_page)
    hoja.merge_page(texto)
    return hoja


def descargar_reporte_pdf(request):
    if request.method != 'POST':
        return HttpResponse("Método no permitido", status=405)

    mes = request.POST.get('mes_descarga')
    semana = request.POST.get('semana_descarga')
    ano = request.POST.get('ano_descarga')
    graficos_seleccionados = request.POST.getlist('grafico')

    reservaciones = Reservacion.objects.all()
    nombre_archivo = "Reporte_Reservaciones"

    if mes and ano:
        if semana:
            first_day = date(int(ano), int(mes), 1)
            first_monday = first_day - timedelta(days=first_day.weekday())
            start_date = first_monday + timedelta(weeks=int(semana) - 1)
            end_date = start_date + timedelta(days=6)
            reservaciones = reservaciones.filter(fecha__range=[start_date, end_date])
            nombre_archivo += f"_Semana_{semana}_Mes_{mes}_Ano_{ano}"
            fecha_rango = f"{start_date.strftime('%d de %B')} al {end_date.strftime('%d de %B de %Y')}"
        else:
            reservaciones = reservaciones.filter(fecha__month=mes, fecha__year=ano)
            nombre_archivo += f"_Mes_{mes}_Ano_{ano}"
            fecha_rango = f"{date(int(ano), int(mes), 1).strftime('%B de %Y')}"
    else:
        nombre_archivo += "_TodosLosDatos"
        fecha_rango = "Todos los registros disponibles"

    graficos_buffers = []

    if 'usuario' in graficos_seleccionados:
        datos = reservaciones.values('usuario__username').annotate(total=Count('id_reservacion')).order_by('-total')
        if datos:
            df = pd.DataFrame({
                'usuario': [d['usuario__username'] for d in datos],
                'cantidad': [d['total'] for d in datos],
            })
            plt.figure(figsize=(10, 6))
            sns.barplot(x='usuario', y='cantidad', data=df, palette='viridis', hue='usuario', legend=False)
            plt.xlabel('Usuario', fontsize=17)
            plt.ylabel('Cantidad', fontsize=17)
            plt.xticks(rotation=0, fontsize=16)
            plt.tight_layout()
            buffer_img = BytesIO()
            plt.savefig(buffer_img, format='png')
            buffer_img.seek(0)
            graficos_buffers.append((buffer_img, "Reservaciones por Usuario"))
            plt.close()

    if 'sala_total' in graficos_seleccionados:
        datos = reservaciones.values('sala__nombre').annotate(total=Count('id_reservacion')).order_by('-total')
        if datos:
            df = pd.DataFrame({
                'sala': [d['sala__nombre'] for d in datos],
                'cantidad': [d['total'] for d in datos],
            })
            plt.figure(figsize=(10, 6))
            sns.barplot(x='sala', y='cantidad', data=df, palette='crest', hue='sala', legend=False)
            plt.xlabel('Sala', fontsize=17)  # Cambia el tamaño de la etiqueta del eje X (sala)
            plt.ylabel('Cantidad', fontsize=17)
            plt.xticks(rotation=0, fontsize=16)
            plt.tight_layout()
            buffer_img = BytesIO()
            plt.savefig(buffer_img, format='png')
            buffer_img.seek(0)
            graficos_buffers.append((buffer_img, "Reservaciones por Sala (Total)"))
            plt.close()

    if 'salas_separado' in graficos_seleccionados:
        for sala in SalaJuntas.objects.all():
            datos = reservaciones.filter(sala=sala).values('usuario__username').annotate(total=Count('id_reservacion')).order_by('-total')
            if datos:
                df = pd.DataFrame({
                    'usuario': [d['usuario__username'] for d in datos],
                    'cantidad': [d['total'] for d in datos],
                })
                plt.figure(figsize=(11, 7))
                sns.barplot(x='usuario', y='cantidad', data=df, palette='mako', hue='usuario', legend=False)
                plt.xlabel('Usuario', fontsize=18)  # Cambia el tamaño de la etiqueta del eje X (sala)
                plt.ylabel('Cantidad', fontsize=18)
                plt.xticks(rotation=0, fontsize=14)
                plt.tight_layout()
                buffer_img = BytesIO()
                plt.savefig(buffer_img, format='png')
                buffer_img.seek(0)
                graficos_buffers.append((buffer_img, f"Reservaciones por Usuario en Sala: {sala.nombre}"))
                plt.close()

    ruta_plantilla = os.path.join(settings.BASE_DIR, 'api', 'report', 'GINP_FORMATO.pdf')
    if not os.path.exists(ruta_plantilla):
        return HttpResponse("No se encontró la plantilla PDF corporativa", status=500)

    plantilla = PdfReader(ruta_plantilla)
    base_page = plantilla.pages[0]
    writer = PdfWriter()

    def render_img_layer(buffer_img, titulo, y_offset):
        temp = BytesIO()
        can = canvas.Canvas(temp, pagesize=letter)
        img = ImageReader(buffer_img)
        iw, ih = img.getSize()
        iw = min(iw, 410)
        ih = iw * (img.getSize()[1] / img.getSize()[0])
        x = (letter[0] - iw) / 2
        y = y_offset  # Ubicación ajustada para mover las imágenes hacia abajo

        can.setFont("Helvetica-Bold", 12)
        can.drawCentredString(letter[0] / 2, y + ih + 15, titulo)
        can.drawImage(img, x, y, width=iw, height=ih)
        can.save()
        return PdfReader(BytesIO(temp.getvalue())).pages[0]


# Generar la primera página con título y resumen
    resumen_texto = (
        f"Rango de fechas: {fecha_rango}    "
        f"Total de reservaciones: {reservaciones.count()}    "
        f"Salas incluidas: {', '.join(sorted(reservaciones.values_list('sala__nombre', flat=True).distinct()))}"
    )
    primera_pagina_base = generar_pagina_resumen(base_page, "Reporte de Reservaciones", resumen_texto)

    # Ahora, añadimos las gráficas debajo del resumen (y más abajo que antes)
    i = 0
    while i < len(graficos_buffers):
        buf1, tit1 = graficos_buffers[i]
        img1 = ImageReader(buf1)
        w1, h1 = img1.getSize()
        h1 = 440 * (h1 / w1)

        usar_primera = (i == 0)

        if i + 1 < len(graficos_buffers):
            buf2, tit2 = graficos_buffers[i + 1]
            img2 = ImageReader(buf2)
            w2, h2 = img2.getSize()
            h2 = 440 * (h2 / w2)
            total_alto = h1 + h2 + 120

            if total_alto <= 700:
                capa = deepcopy(primera_pagina_base if usar_primera else base_page)
                capa.merge_page(render_img_layer(buf1, tit1, y_offset=380))  # Ajustar la posición de las imágenes
                capa.merge_page(render_img_layer(buf2, tit2, y_offset=100))
                writer.add_page(capa)
                i += 2
                continue

        capa = deepcopy(primera_pagina_base if usar_primera else base_page)
        capa.merge_page(render_img_layer(buf1, tit1, y_offset=390))  # Ajuste del primer gráfico
        writer.add_page(capa)
        i += 1


    output = BytesIO()
    writer.write(output)
    response = HttpResponse(output.getvalue(), content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}.pdf"'
    return response




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
                reservas_url = request.build_absolute_uri(reverse('reservas_semanales'))
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
                            <p>Puedes checar las reservaciones para esta semana en este enlace: <a href="{reservas_url}">Reservas semanales</a></p>
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
                        <p>Puedes checar las reservaciones para esta semana en este enlace: <a href="{reservas_url}">Reservas semanales</a></p>
                        <p>Atentamente,</p>
                        <p>{request.user.username}</p>
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
    ahora = datetime.now()
    anio, semana, _ = hoy.isocalendar()

    # Obtener reservaciones de la semana actual
    reservas = Reservacion.objects.filter(
        fecha__week=semana,
        fecha__year=anio
    ).exclude(
        fecha__lt=hoy
    ).exclude(
        fecha=hoy,
        hora_final__lt=ahora.time()
    ).order_by('fecha', 'hora_inicio')

    # Agregar banderas en_curso y proxima
    for r in reservas:
        inicio = datetime.combine(r.fecha, r.hora_inicio)
        fin = datetime.combine(r.fecha, r.hora_final)

        r.en_curso = inicio <= ahora <= fin
        r.proxima = False

        if not r.en_curso and inicio > ahora:
            minutos_restantes = (inicio - ahora).total_seconds() / 60
            if minutos_restantes <= 30:
                r.proxima = True

    # Agrupar por semana (se mantiene la estructura)
    semanas = defaultdict(list)
    for r in reservas:
        año_r, semana_r, _ = r.fecha.isocalendar()
        semanas[(año_r, semana_r)].append(r)

    return semanas

def vista_reservas_semanales(request):
    semanas_reservas = obtener_semanas_reservaciones()

    datos = []
    for (anio, semana), reservas in semanas_reservas.items():
        primer_dia_semana = date.fromisocalendar(anio, semana, 1)
        ultimo_dia_semana = primer_dia_semana + timedelta(days=6)
        datos.append({
            'rango': f"Semana del {primer_dia_semana.strftime('%d %b')} al {ultimo_dia_semana.strftime('%d %b')}",
            'reservas': reservas
        })

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
    reservas_url = request.build_absolute_uri(reverse('reservas_semanales'))

    # Enviar correo a admin con motivo
    subject_admin = f"Reservación eliminada: {reservacion.evento}"
    message_admin = f"""
        <h2>🗑️ Notificación de Eliminación de Reservación</h2>
        <p>Estimado/a administrador,</p>
        <p>La reservación para <strong>{reservacion.evento}</strong> ha sido eliminada.</p>
        <h3>Detalles de la Reservación eliminada:</h3>
        <ul>
            <li>📆 Fecha: {reservacion.fecha}</li>
            <li>🕒 Hora de inicio: {reservacion.hora_inicio}</li>
            <li>🕒 Hora de finalización: {reservacion.hora_final}</li>
            <li>🏢 Sala: {reservacion.sala}</li>
        </ul>
        <p>Motivo de eliminación: <strong>{motivo}</strong></p>
        <p>Puedes checar las reservaciones actuales en este enlace: <a href="{reservas_url}">Reservas</a></p>
        <p>Atentamente,</p>
        <p>{request.user.username}</p>
    """
    send_mail(subject_admin, "", 'informatica.cdt.stc@gmail.com', ['eliasaranda055@gmail.com'], html_message=message_admin)
    
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
            <p>Puedes checar las reservaciones actuales en este enlace: <a href="{reservas_url}">Reservas</a></p>
            <p>Atentamente,</p>
            <p>{request.user.username}</p>
        """
        send_mail(subject, "", 'informatica.cdt.stc@gmail.com', [invitado.correo], html_message=message)
    
    reservacion.delete()
    return JsonResponse({'success': True})