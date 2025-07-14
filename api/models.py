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

class Empleado(models.Model):
    empleado_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    numero_empleado = models.CharField(max_length=20, unique=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    id_area = models.ForeignKey(Area, on_delete=models.CASCADE)  

    class Meta:
        db_table = 'empleados'

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"
    

class Invitado(models.Model):
    id_invitado = models.AutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=200)
    correo = models.EmailField(unique=True)  
    id_area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="invitados")

    class Meta:
        db_table = 'invitados'

    def __str__(self):
        return self.nombre_completo

class SalaJuntas(models.Model):
    id_sala = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    equipo = models.TextField()
    capacidad = models.PositiveIntegerField()

    class Meta:
        db_table = 'salas_juntas'

    def __str__(self):
        return f"{self.nombre}"

class Reservacion(models.Model):
    id_reservacion = models.AutoField(primary_key=True)
    evento = models.CharField(max_length=200)
    comentarios = models.TextField(blank=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_final = models.TimeField()
    sala = models.ForeignKey(SalaJuntas, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    enviar_correo = models.BooleanField(default=False)  
    monitorear = models.BooleanField(default=True) 

    class Meta:
        db_table = 'reservaciones'

    def __str__(self):
        return f"{self.evento} - {self.fecha}"

class ReservacionInvitado(models.Model):
    id_reservacion_invitado = models.AutoField(primary_key=True)
    reservacion = models.ForeignKey(Reservacion, on_delete=models.CASCADE) 
    invitado = models.ForeignKey(Invitado, on_delete=models.CASCADE)  

    class Meta:
        db_table = 'reservacion_invitados'
        unique_together = ('reservacion', 'invitado') 

    def __str__(self):
        return f"{self.invitado.nombre_completo} en {self.reservacion.evento}"


class ConteoPersonas(models.Model):
    id_conteo = models.AutoField(primary_key=True)
    reservacion = models.ForeignKey(Reservacion, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='conteos/')
    personas_contadas = models.PositiveIntegerField()
    fecha = models.DateField()

    class Meta:
        db_table = 'conteos_personas'

    def __str__(self):
        return f"Conteo {self.id_conteo} - {self.personas_contadas} personas"


