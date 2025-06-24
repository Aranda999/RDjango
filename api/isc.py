from icalendar import Calendar, Event, vRecur
from datetime import datetime, timedelta
from io import BytesIO
from pytz import timezone, utc

def generar_ics(evento, sala, comentarios, fechas, hora_inicio, hora_fin, organizador_email):
    cal = Calendar()
    cal.add('prodid', '-//Sistema de Reservas//mx')
    cal.add('version', '2.0')

    if not fechas:
        return None

    fechas_ordenadas = sorted(fechas)
    primera_fecha = fechas_ordenadas[0]
    ultima_fecha = fechas_ordenadas[-1]

    tz_local = timezone("America/Mexico_City")
    dtstart = tz_local.localize(datetime.combine(primera_fecha, hora_inicio))
    dtend = tz_local.localize(datetime.combine(primera_fecha, hora_fin))

    # 🔧 Asegurar inclusión de la última fecha recurrente
    until_utc = utc.localize(datetime.combine(ultima_fecha, hora_inicio) + timedelta(minutes=1))

    evento_ical = Event()
    evento_ical.add('summary', evento)
    evento_ical.add('location', sala)
    evento_ical.add('description', comentarios)
    evento_ical.add('dtstart', dtstart)
    evento_ical.add('dtend', dtend)
    evento_ical.add('dtstamp', datetime.now(tz_local))
    evento_ical.add('organizer', f'MAILTO:{organizador_email}')

    evento_ical.add('rrule', vRecur({
        'FREQ': 'WEEKLY',
        'UNTIL': until_utc
    }))

    cal.add_component(evento_ical)

    output = BytesIO()
    output.write(cal.to_ical())
    output.seek(0)
    return output
