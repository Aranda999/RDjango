from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

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
    return render(request, template_name=template_view)
