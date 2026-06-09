from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect


class BlockBannedUsersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            logout(request)
            messages.error(request, "Ladmin banak. Ma9aderch tb9a connecte.")
            return redirect('login')
        return self.get_response(request)
