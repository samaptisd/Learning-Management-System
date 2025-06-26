from django.shortcuts import redirect
from django.conf import settings

class SessionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            if request.path not in [settings.LOGIN_URL, '/accounts/login/']:  # Adjust if necessary
                return redirect(settings.LOGIN_URL)  # Redirect to login page when session expires

        return self.get_response(request)