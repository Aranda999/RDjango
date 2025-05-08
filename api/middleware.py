# middleware.py
import datetime
from django.contrib import messages
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect

class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        try:
            last_activity = request.session['last_activity']
        except KeyError:
            last_activity = None

        if last_activity:
            now = datetime.datetime.now()
            last_activity_time = datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            time_diff = now - last_activity_time

            if time_diff.total_seconds() > 300:
                logout(request)
                messages.error(request, "Se cerro tu sesion por inactividad.")
                return redirect('login')

        request.session['last_activity'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')