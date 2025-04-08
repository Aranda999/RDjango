# models.py
from django.db import models
from django.contrib.auth.models import User


# DECLARACION DE QUE USUARIOS PUEDEN VER EL HOME
class HomePermission(models.Model):
    class Meta:
        permissions = [
            ("Home", "Puede ver el home"),
        ]








#TABLA DE INFORMACION DE LOS USUARIOS
# class Empleado(models.Model):
#     num_empleado = models.AutoField(primary_key=True)
#     nombre = models.CharField(max_length=50)
#     apellido_paterno = models.CharField(max_length=50)
#     apellido_materno = models.CharField(max_length=50)
#     usuario = models.OneToOneField(User, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.nombre + ' ' + self.apellido_paterno + ' ' + self.apellido_materno