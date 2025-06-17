"""
URL configuration for DjangoApi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import reverse
from django.urls import path, reverse_lazy
from django.urls import path
from api.home.home_view import Home
from api.security.security_view import HomeUser
from api.home.home_view import Reservation
from api.tools.tools_view import editar_reservacion
from api.home.home_view import get_ocupados
from api.home.home_view import Notificaciones
from api.log.login_view import Login
from api.log.login_view import Logout
from api.tools.tools_view import graficos
from api.tools.tools_view import get_destinatarios_por_area
from api.tools.tools_view import get_invitados
from api.tools.tools_view import eliminar_reservacion
from api.tools.tools_view import guardar_invitados
from api.tools.tools_view import vista_reservas_semanales
from api.tools.tools_view import enviar_notificacion
from api.tools.tools_view import descargar_reporte_pdf
from api.security.security_view import Password
from api.security.security_view import reset_password
from api.video.video_view import camera_view
from api.controller.control_view import administracion
from django.contrib.auth.decorators import login_required 

admin.site.login_url = reverse_lazy('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',Login, name= "login"),
    path('logout/',Logout, name= "logout"), 
    path('home/',Home, name= "home"),
    path('homeuser/',HomeUser, name= "homeuser"),
    path('password/',Password, name= "password"),
    path('reservation/',Reservation, name= "reservation"),
    path('editar-reservacion/<int:pk>/', editar_reservacion, name='editar_reservacion'),
    path('graficos/',graficos, name= "graficos"),
    path('reset-password/<uidb64>/<token>/', reset_password, name='reset_password'),
    path('get_ocupados/', get_ocupados, name='get_ocupados'),
    path('get_destinatarios/', get_destinatarios_por_area, name='get_destinatarios'),
    path('get_invitados/', get_invitados, name='get_invitados'),
    path('guardar_invitados/', guardar_invitados, name='guardar_invitados'),
    path('reservas-publico/', vista_reservas_semanales, name='reservas_semanales'),
    path('notificacion/', Notificaciones, name='notificacion'),
    path('enviar_notificacion/', enviar_notificacion, name='enviar_notificacion'),
    path('camera/', camera_view, name='camera_view'),
    path('administracion/', administracion, name='administracion'),
    path('eliminar_reservacion/<int:pk>/', eliminar_reservacion, name='eliminar_reservacion'),
    path('descargar-reporte-pdf/', descargar_reporte_pdf, name='descargar_reporte_pdf'),

]


