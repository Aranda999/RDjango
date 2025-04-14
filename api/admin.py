from django.contrib import admin
from .models import Empleado, Area, SalaJuntas, Reservacion, Invitado

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido_paterno', 'apellido_materno', 'numero_empleado')
    search_fields = ('nombre', 'apellido_paterno', 'numero_empleado')
    list_filter = ('usuario',)

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id_area', 'nombre')
    search_fields = ('id_area', 'nombre')

@admin.register(SalaJuntas)
class SalaJuntasAdmin(admin.ModelAdmin):
    list_display = ('id_sala', 'nombre', 'capacidad')
    search_fields = ('id_sala', 'nombre')

@admin.register(Invitado)
class InvitadoAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'correo')
    search_fields = ('nombre_completo', 'correo')

@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    list_display = ('evento', 'fecha', 'hora_inicio', 'hora_final', 'area', 'sala')
    search_fields = ('evento',)
    list_filter = ('fecha', 'area', 'sala')
    filter_horizontal = ('invitados',)
