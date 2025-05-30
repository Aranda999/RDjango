from django.shortcuts import render, redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import login
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash, logout
from django.core.mail import send_mail


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

def Password(request):
    template_name = "pass-reset.html"
    if request.method == 'POST':
        email = request.POST['email']
        try:
            # Busca el usuario que tenga asociado el email ingresado
            user = User.objects.get(email=email)
            
            # Generar el uid token y se importa la libreria hasta arriba
            uid = urlsafe_base64_encode(str(user.pk).encode())
            token = PasswordResetTokenGenerator().make_token(user)

            # Enlace para restablecer y obtiene el domino actual el localhost
            domain = request.get_host()  
            reset_url = f"http://{domain}/reset-password/{uid}/{token}/"

            # Mensaje del correo que se encuentra en el html correspondiente 
            subject = "Restablece tu contraseña"
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })

            # Envia correo
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            # Mensajes sea la situacion que sea
            return render(request, template_name, {'mensaje': 'Correo enviado con éxito'})
        
        except User.DoesNotExist:
            return render(request, template_name, {'error': 'Correo electrónico no encontrado'})
        
    return render(request, template_name)


def reset_password(request, uidb64, token):
    try:
        # Decodificar el UID del usuario
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and PasswordResetTokenGenerator().check_token(user, token):
        # Si el token es válido, loguear al usuario directamente 
        login(request, user)  
        # Redirigir al homeuser
        return redirect('homeuser') 
    else:
        # Agregar mensaje de error a la sesión y redirigir a la página de login
        error_message = mark_safe('El enlace es inválido o ya ha expirado.<br> Por favor, solicita un nuevo enlace.')
        messages.error(request, error_message) 
        return redirect('login') 
