from django.contrib.auth.decorators import login_required
from functools import wraps
from django.core.exceptions import PermissionDenied

def cashier_or_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ['cashier', 'admin']:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper

def cashier_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'cashier':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper
