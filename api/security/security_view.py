from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.models import User
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import login
from django.contrib import messages
from django.utils.safestring import mark_safe


def Password(request):
    template_name = "pass-reset.html"
    if request.method == 'POST':
        email = request.POST['email']
        try:
            # Obtener al usuario por su email
            user = User.objects.get(email=email)
            
            # Generar el uid (usuario codificado) y token
            uid = urlsafe_base64_encode(str(user.pk).encode())
            token = PasswordResetTokenGenerator().make_token(user)

            # Crear el enlace de restablecimiento
            domain = request.get_host()  # Obtener el dominio actual, por ejemplo: localhost:8000
            reset_url = f"http://{domain}/reset-password/{uid}/{token}/"

            # Crear el contenido del correo
            subject = "Restablece tu contraseña"
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })

            # Enviar el correo
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            # Mostrar un mensaje de éxito
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
        login(request, user)  # Esto autentica al usuario automáticamente
        # Redirigir al homeuser (o a donde desees)
        return redirect('homeuser')  # Cambia 'homeuser' por el nombre de la URL a la que quieras redirigir
    else:
        # Agregar mensaje de error a la sesión y redirigir a la página de login
        error_message = mark_safe('El enlace es inválido o ya ha expirado.<br> Por favor, solicita un nuevo enlace.')
        messages.error(request, error_message)  # Agregar mensaje a la sesión
        return redirect('login')  # Redirigir al login
