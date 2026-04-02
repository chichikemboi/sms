from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Restrict a view to users with any of the given roles (or admin)."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_admin or request.user.role in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'You do not have permission to access that page.')
            return redirect('dashboard:home')
        return wrapper
    return decorator


def admin_required(view_func):
    """Restrict a view to admins only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_admin:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'This area is restricted to administrators.')
        return redirect('dashboard:home')
    return wrapper


def teacher_required(view_func):
    """Restrict a view to class teachers, subject teachers, and admins."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_admin or request.user.is_any_teacher:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'This area is for teaching staff only.')
        return redirect('dashboard:home')
    return wrapper
