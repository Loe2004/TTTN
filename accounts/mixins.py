"""Role-based access control (RBAC) helpers.

Provides class-based-view mixins and function-view decorators that restrict
access based on the user's ``role`` (see ``accounts.models.User.Role``).
"""

from functools import wraps

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin):
    """Restrict a CBV to users whose role is in ``allowed_roles``.

    Superusers always pass. Unauthenticated users are redirected to login
    (via ``LoginRequiredMixin``); authenticated users without the right role
    get a 403.
    """

    allowed_roles: tuple[str, ...] = ()

    def dispatch(self, request, *args, **kwargs):
        # Let LoginRequiredMixin handle unauthenticated users first.
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        if not self.has_role(request.user):
            raise PermissionDenied("You do not have permission to access this page.")

        return super().dispatch(request, *args, **kwargs)

    def has_role(self, user) -> bool:
        if user.is_superuser:
            return True
        if not self.allowed_roles:
            return True
        return user.role in self.allowed_roles


class AdminRequiredMixin(RoleRequiredMixin):
    """Only Admin (or superuser) may access."""

    allowed_roles = ("admin",)


class ManagerRequiredMixin(RoleRequiredMixin):
    """Admin and Manager may access."""

    allowed_roles = ("admin", "manager")


class StaffRequiredMixin(RoleRequiredMixin):
    """Admin, Manager and Technician may access (everyone except Viewer)."""

    allowed_roles = ("admin", "manager", "technician")


def role_required(*roles):
    """Decorator for function-based views requiring one of ``roles``.

    Superusers always pass.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login

                return redirect_to_login(request.get_full_path())
            if not (user.is_superuser or not roles or user.role in roles):
                raise PermissionDenied(
                    "You do not have permission to access this page."
                )
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
