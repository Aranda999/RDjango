# models.py
from django.db import models
from django.contrib.auth.models import User


# DECLARACION DE QUE USUARIOS PUEDEN VER EL HOME
class HomePermission(models.Model):
    class Meta:
        permissions = [
            ("Home", "Puede ver el home"),
        ]


#TABLAS DE BD

# Tabla: Personas (Empleados)
class Empleado(models.Model):
    empleado_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    numero_empleado = models.CharField(max_length=20, unique=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'empleados'

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"


# Tabla: Áreas (con clave primaria manual)
class Area(models.Model):
    id_area = models.CharField(
        primary_key=True,
        max_length=10,
        verbose_name="ID de Área (abreviatura)"
    )
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'areas'

    def __str__(self):
        return f"{self.id_area} - {self.nombre}"


# Tabla: Salas de Juntas (con ID manual)
class SalaJuntas(models.Model):
    id_sala = models.CharField(
        primary_key=True,
        max_length=10,
        verbose_name="ID de Sala (abreviatura)"
    )
    nombre = models.CharField(max_length=100)
    equipo = models.TextField()
    capacidad = models.PositiveIntegerField()

    class Meta:
        db_table = 'salas_juntas'

    def __str__(self):
        return f"{self.id_sala} - {self.nombre}"


# Tabla: Invitados externos (solo nombre y correo)
class Invitado(models.Model):
    id_invitado = models.AutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=200)
    correo = models.EmailField()

    class Meta:
        db_table = 'invitados'

    def __str__(self):
        return self.nombre_completo


# Tabla: Reservaciones
class Reservacion(models.Model):
    id_reservacion = models.AutoField(primary_key=True)
    evento = models.CharField(max_length=200)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    comentarios = models.TextField(blank=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_final = models.TimeField()
    sala = models.ForeignKey(SalaJuntas, on_delete=models.CASCADE)
    invitados = models.ManyToManyField(Invitado, blank=True)

    class Meta:
        db_table = 'reservaciones'

    def __str__(self):
        return f"Reservación: {self.evento} - {self.fecha}"
