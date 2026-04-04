# admin_panel/utils.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils.timezone import now
from core.utils import get_client_ip   # ✅ reuse function
from cashier.models import UserSessionLog

def login_logger(sender, request, user, **kwargs):
    session_log = UserSessionLog.objects.create(
        user=user,
        ip_address=get_client_ip(request),   # ✅ same helper
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )
    request.session["session_log_id"] = session_log.id

def logout_logger(sender, request, user, **kwargs):
    session_log_id = request.session.get("session_log_id")
    if session_log_id:
        try:
            log = UserSessionLog.objects.get(id=session_log_id)
            log.logout_time = now()
            log.save(update_fields=["logout_time"])
        except UserSessionLog.DoesNotExist:
            pass

# Connect signals
user_logged_in.connect(login_logger)
user_logged_out.connect(logout_logger)
