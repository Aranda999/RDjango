# admin.py
from django.contrib import admin
from .models import Area, Empleado, SalaJuntas, Invitado, Reservacion

# Personalizando la vista de administración para el modelo Area
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id_area', 'nombre')  # Qué campos mostrar en la lista
    search_fields = ('id_area', 'nombre')  # Permite buscar por ID de área o nombre
    list_filter = ('nombre',)  # Filtros en la barra lateral
    ordering = ('nombre',)  # Orden de los registros en la vista de lista

# Personalizando la vista de administración para el modelo Empleado
@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('empleado_id', 'nombre', 'apellido_paterno', 'numero_empleado', 'id_area')
    search_fields = ('nombre', 'apellido_paterno', 'numero_empleado')
    list_filter = ('id_area',)  # Filtrar por área
    ordering = ('apellido_paterno', 'apellido_materno')  # Ordenar por apellido

# Personalizando la vista de administración para el modelo SalaJuntas
@admin.register(SalaJuntas)
class SalaJuntasAdmin(admin.ModelAdmin):
    list_display = ('id_sala', 'nombre', 'capacidad')
    search_fields = ('nombre',)
    list_filter = ('capacidad',)  # Filtrar por capacidad
    ordering = ('nombre',)

# Personalizando la vista de administración para el modelo Invitado
@admin.register(Invitado)
class InvitadoAdmin(admin.ModelAdmin):
    list_display = ('id_invitado', 'nombre_completo', 'correo', 'id_area')
    search_fields = ('nombre_completo', 'correo')
    list_filter = ('id_area',)  # Filtrar por área
    ordering = ('nombre_completo',)

# Personalizando la vista de administración para el modelo Reservacion
@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    list_display = ('id_reservacion', 'evento', 'fecha', 'hora_inicio', 'hora_final', 'sala')
    search_fields = ('evento',)
    list_filter = ('fecha', 'sala')  # Filtrar por fecha y sala
    ordering = ('fecha', 'hora_inicio')  # Ordenar por fecha y hora de inicio
    filter_horizontal = ('invitados',)  # Mejora la interfaz para seleccionar invitados (para ManyToManyField)
