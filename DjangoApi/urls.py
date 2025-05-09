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
from django.urls import path, reverse_lazy
from django.urls import path
from api.home.home_view import Home
from api.home.home_view import HomeUser
from api.home.home_view import Reservation
from api.home.home_view import editar_reservacion
from api.home.home_view import get_ocupados
from api.log.login_view import Login
from api.log.login_view import Logout
from api.tools.tools_view import graficos
from api.security.security_view import Password
from api.security.security_view import reset_password
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
    path('reservation/editar/<int:pk>/', editar_reservacion, name='editar_reservacion'),
    path('graficos/',graficos, name= "graficos"),
    path('reset-password/<uidb64>/<token>/', reset_password, name='reset_password'),
    path('get_ocupados/', get_ocupados, name='get_ocupados'),
]


