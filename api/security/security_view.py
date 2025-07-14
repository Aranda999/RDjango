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

        if nueva_contrasena != confirmar_contrasena:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'home-user.html')  

        # guardar nueva contraseña
        user = request.user
        user.set_password(nueva_contrasena)
        user.save()

        update_session_auth_hash(request, user)

        # cerrar sesion
        logout(request)

        messages.success(request, "Contraseña cambiada. Por favor, vuelve a iniciar sesión.")
        return redirect('login') 
    return render(request, 'home-user.html')

def Password(request):
    template_name = "pass-reset.html"
    if request.method == 'POST':
        email = request.POST['email']
        try:
            # busqueda de usuario por email
            user = User.objects.get(email=email)
            # generacion del token
            uid = urlsafe_base64_encode(str(user.pk).encode())
            token = PasswordResetTokenGenerator().make_token(user)

            # enlace 
            domain = request.get_host()  
            reset_url = f"http://{domain}/reset-password/{uid}/{token}/"

            # html que contiene el mensaje para enviar
            subject = "Restablece tu contraseña"
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })

            # Envia correo
            send_mail(
                subject,
                '',
                settings.EMAIL_HOST_USER,
                [email],
                html_message=message,
            )

            # manejo de mensaje
            return render(request, template_name, {'mensaje': 'Correo enviado con éxito'})
        
        except User.DoesNotExist:
            return render(request, template_name, {'error': 'Correo electrónico no encontrado'})
        
    return render(request, template_name)


def reset_password(request, uidb64, token):
    try:
        # Busca al usuario
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

        # Sentencia de control para validar 
    if user is not None and PasswordResetTokenGenerator().check_token(user, token):
        login(request, user)  
        return redirect('homeuser') 
    else:
        # Manejo de mensaje al usuario
        error_message = mark_safe('El enlace es inválido o ya ha expirado.<br> Por favor, solicita un nuevo enlace.')
        messages.error(request, error_message) 
        return redirect('login') 
