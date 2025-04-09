from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages


@login_required
def Home(request):
    if request.user.is_superuser:
        template_view = "home.html"
        return render(request, template_name=template_view)
    else:
        return redirect("homeuser")
    

@login_required
def HomeUser(request):
    template_view = "home-user.html"
    
    if request.method == 'POST':
        nueva_contrasena = request.POST.get('nuevaContrasena')
        confirmar_contrasena = request.POST.get('confirmarContrasena')

        # Validación para verificar que las contraseñas coinciden
        if nueva_contrasena != confirmar_contrasena:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('homeuser')

        # Actualizar la contraseña del usuario
        usuario = request.user
        usuario.set_password(nueva_contrasena)
        usuario.save()

        messages.success(request, "Contraseña cambiada con éxito.")
        return redirect('login')  # Redirige después de un cambio exitoso

    return render(request, template_name=template_view)
