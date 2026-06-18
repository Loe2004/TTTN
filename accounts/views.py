"""Authentication and user-management views.

- Public registration is disabled (admin-managed users only).
- Login / logout / password change / password reset use Django's built-in
  auth views with styled forms and custom templates.
- Admin-only User Management provides list / create / update / delete.
"""

from django.contrib import messages
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from .forms import (
    LoginForm,
    ProfileForm,
    StyledPasswordChangeForm,
    StyledPasswordResetForm,
    StyledSetPasswordForm,
    UserCreateForm,
    UserUpdateForm,
)
from .mixins import AdminRequiredMixin

User = get_user_model()


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    pass


class PasswordChangeView(SuccessMessageMixin, auth_views.PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = StyledPasswordChangeForm
    success_url = reverse_lazy("accounts:profile")
    success_message = "Đổi mật khẩu thành công."


# --- Forgot password flow ---------------------------------------------------
class PasswordResetView(auth_views.PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    form_class = StyledPasswordResetForm
    success_url = reverse_lazy("accounts:password_reset_done")


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = StyledSetPasswordForm
    success_url = reverse_lazy("accounts:password_reset_complete")


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


# ---------------------------------------------------------------------------
# Profile (self-service)
# ---------------------------------------------------------------------------
class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "accounts/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("accounts:profile")
    success_message = "Cập nhật hồ sơ thành công."

    def get_object(self, queryset=None):
        return self.request.user


# ---------------------------------------------------------------------------
# User management (Admin only) — replaces public registration
# ---------------------------------------------------------------------------
class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 20
    ordering = ("-date_joined",)

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get("q", "").strip()
        if search:
            from django.db.models import Q

            qs = qs.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        return qs


class UserCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")
    success_message = "Tạo người dùng thành công."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Thêm người dùng"
        return ctx


class UserUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")
    success_message = "Cập nhật người dùng thành công."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Sửa người dùng"
        return ctx


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = "accounts/user_confirm_delete.html"
    success_url = reverse_lazy("accounts:user_list")

    def get_queryset(self):
        # Prevent an admin from deleting their own account (even via direct URL).
        return super().get_queryset().exclude(pk=self.request.user.pk)

    def form_valid(self, form):
        self.object.is_active = False
        self.object.save()
        messages.success(self.request, "Đã khóa người dùng.")
        return redirect(self.success_url)


class UserBulkDeactivateView(AdminRequiredMixin, View):
    def post(self, request):
        ids = request.POST.get("ids", "").split(",")
        valid_ids = [i for i in ids if i.isdigit() and int(i) != request.user.pk]
        if valid_ids:
            count = User.objects.filter(id__in=valid_ids).update(is_active=False)
            messages.success(request, f"Đã khóa {count} người dùng.")
        return redirect("accounts:user_list")


# ---------------------------------------------------------------------------
# Dashboard with statistics (Phase 7)
# ---------------------------------------------------------------------------
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        from devices.models import Category, Device, Location, MaintenanceLog

        ctx = super().get_context_data(**kwargs)
        devices = Device.objects.all()
        status_counts = {
            "active": devices.filter(status=Device.Status.ACTIVE).count(),
            "maintenance": devices.filter(
                status=Device.Status.MAINTENANCE
            ).count(),
            "broken": devices.filter(status=Device.Status.BROKEN).count(),
        }
        ctx["total_devices"] = devices.count()
        ctx["status_counts"] = status_counts
        ctx["total_categories"] = Category.objects.count()
        ctx["total_locations"] = Location.objects.count()
        ctx["recent_devices"] = devices.select_related("category", "location")[:5]
        ctx["recent_logs"] = MaintenanceLog.objects.select_related(
            "device", "performed_by"
        )[:5]
        # Devices grouped by category (for a simple breakdown chart).
        ctx["by_category"] = list(
            Category.objects.values("name").annotate(
                count=models.Count("devices")
            )
        )
        return ctx
