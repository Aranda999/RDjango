import os
import sys
import django
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist

# Configuración de entorno
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoApi.settings')
django.setup()

# Importa modelos
from api.models import Reservacion, SalaJuntas
from django.contrib.auth.models import User

# Carga el archivo CSV
csv_path = r'C:\Users\elias\Downloads\ELIAS\RESIDENCIA\proyecto\api\reservaciones.csv'
df = pd.read_csv(csv_path)

# Convierte fechas y horas a tipos nativos
df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True).dt.date
df['hora_inicio'] = pd.to_datetime(df['hora_inicio'], format='%H:%M:%S').dt.time
df['hora_final'] = pd.to_datetime(df['hora_final'], format='%H:%M:%S').dt.time

# Inserta reservaciones una a una
for index, row in df.iterrows():
    try:
        sala = SalaJuntas.objects.get(nombre=row['sala_id'])  # ajusta si el campo es diferente
    except ObjectDoesNotExist:
        print(f"❌ Sala no encontrada: '{row['sala_id']}' en fila {index}")
        continue

    usuario = None
    if not pd.isnull(row['usuario_id']):
        try:
            usuario = User.objects.get(username=row['usuario_id'])  # ajusta si es otro identificador
        except ObjectDoesNotExist:
            print(f"⚠️ Usuario no encontrado: '{row['usuario_id']}' en fila {index}")
            continue

    reservacion = Reservacion(
        evento=row['evento'],
        comentarios=row['comentarios'],
        fecha=row['fecha'],
        hora_inicio=row['hora_inicio'],
        hora_final=row['hora_final'],
        sala=sala,
        usuario=usuario,
        enviar_correo=row['enviar_correo'] == 1
    )
    reservacion.save()

print("✅ Reservaciones insertadas correctamente.")
