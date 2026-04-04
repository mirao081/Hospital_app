# core/middleware.py

from .models import AccessLog
from django.utils.timezone import now
from .utils import get_client_ip  

class AccessLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            AccessLog.objects.create(
                user=request.user,
                path=request.path,
                method=request.method,
                ip_address=get_client_ip(request),  # ✅ use utils function
                timestamp=now()
            )
        return response

    