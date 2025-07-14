from django.contrib import admin
from .models import Area, Empleado, SalaJuntas, Invitado, Reservacion, ReservacionInvitado
from django.contrib.admin import AdminSite


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id_area', 'nombre')  
    search_fields = ('id_area', 'nombre')  
    list_filter = ('nombre',)  
    ordering = ('nombre',)  

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('empleado_id', 'nombre', 'apellido_paterno', 'numero_empleado', 'id_area')
    search_fields = ('nombre', 'apellido_paterno', 'numero_empleado')
    list_filter = ('id_area',)  
    ordering = ('apellido_paterno', 'apellido_materno')  

@admin.register(SalaJuntas)
class SalaJuntasAdmin(admin.ModelAdmin):
    list_display = ('id_sala', 'nombre', 'capacidad')
    search_fields = ('nombre',)
    list_filter = ('capacidad',)  
    ordering = ('nombre',)

@admin.register(Invitado)
class InvitadoAdmin(admin.ModelAdmin):
    list_display = ('id_invitado', 'nombre_completo', 'correo', 'id_area')
    search_fields = ('nombre_completo', 'correo')
    list_filter = ('id_area',)  
    ordering = ('nombre_completo',)

class ReservacionInvitadoInline(admin.TabularInline):
    model = ReservacionInvitado
    extra = 1

@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    list_display = ('evento', 'fecha', 'hora_inicio', 'hora_final', 'sala', 'usuario')
    search_fields = ('evento', 'fecha')
    list_filter = ('fecha', 'sala','usuario')
    inlines = [ReservacionInvitadoInline]

@admin.register(ReservacionInvitado)
class ReservacionInvitadoAdmin(admin.ModelAdmin):
    list_display = ('reservacion', 'invitado')
    search_fields = ('reservacion__evento', 'invitado__nombre_completo')