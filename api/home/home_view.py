from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required



@login_required (login_url= 'login')
def Home(request):
    if request.user.is_superuser:
        template_view = "home.html"
        return render(request, template_name=template_view)
    else:
        return redirect("homeuser")

@login_required
def HomeUser(request):
    if request.method == 'POST':
        nueva_contrasena = request.POST.get('nuevaContrasena')
        confirmar_contrasena = request.POST.get('confirmarContrasena')

        # Verificar si las contraseñas coinciden
        if nueva_contrasena != confirmar_contrasena:
            # Mensaje de error que se mostrará en el modal
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'home-user.html')  # Mantener el modal abierto

        # Si las contraseñas coinciden, cambiar la contraseña del usuario
        user = request.user
        user.set_password(nueva_contrasena)
        user.save()

        # Actualizar la sesión para que no se cierre después de cambiar la contraseña
        update_session_auth_hash(request, user)

        # Cerrar sesión del usuario
        logout(request)

        # Mensaje de éxito y redirigir al login
        messages.success(request, "Contraseña cambiada exitosamente. Por favor, vuelve a iniciar sesión.")
        return redirect('login')  # Redirige al login después de cerrar sesión

    # Si no es un POST, solo se muestra el formulario
    return render(request, 'home-user.html')