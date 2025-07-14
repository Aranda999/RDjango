from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

# Vista Login
def Login(request):
    template_name = "signin.html"
    # POST
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        # comparacion de inicio
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('home')
            else:
                return redirect('homeuser')
        else:
            return render(request, template_name, {'error': 'Credenciales inválidas'})
    return render(request, template_name)

def Logout(request):
    logout(request)
    return redirect('login')  

