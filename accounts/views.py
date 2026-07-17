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
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from devices.models import Device, DeviceHistory

from .forms import (
    LoginForm,
    ProfileForm,
    RegisterForm,
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

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_approved and not user.is_superuser and user.role != User.Role.ADMIN:
            messages.error(self.request, "Tài khoản của bạn đang chờ admin duyệt.")
            return redirect("accounts:login")
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or user.role == User.Role.ADMIN:
            return reverse("accounts:admin_dashboard")
        return super().get_success_url()


class LogoutView(auth_views.LogoutView):
    pass


class RegisterView(SuccessMessageMixin, CreateView):
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("accounts:login")
    success_message = "Đăng ký thành công. Tài khoản của bạn đang chờ admin duyệt."

    def form_valid(self, form):
        user = form.save(commit=False)
        # New registrations are pending approval and inactive until an admin approves.
        user.is_approved = False
        user.is_rejected = False
        user.is_active = False
        # Respect chosen role from the form (form restricts choices, excludes admin)
        role = form.cleaned_data.get("role")
        if role:
            user.role = role
        user.save()
        # Store the registered user's id in session so we can show a status page
        self.request.session["registered_user_id"] = user.pk
        return redirect("accounts:register_status")


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

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_approved = True
        user.save()
        return super().form_valid(form)

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


class UserUnlockView(AdminRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user != request.user:
            user.is_active = True
            user.save()
            messages.success(request, f"Đã mở khóa người dùng {user.username}.")
        return redirect("accounts:user_list")


class UserBulkActivateView(AdminRequiredMixin, View):
    def post(self, request):
        ids = request.POST.get("ids", "").split(",")
        valid_ids = [i for i in ids if i.isdigit() and int(i) != request.user.pk]
        if valid_ids:
            count = User.objects.filter(id__in=valid_ids).update(is_active=True)
            messages.success(request, f"Đã mở khóa {count} người dùng.")
        return redirect("accounts:user_list")


# ---------------------------------------------------------------------------
# Dashboard with statistics (Phase 7)
# ---------------------------------------------------------------------------
class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = "accounts/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["pending_users"] = (
            User.objects.filter(is_approved=False, is_rejected=False)
            .exclude(role=User.Role.ADMIN)
        )
        ctx["all_users"] = User.objects.exclude(role=User.Role.ADMIN).order_by("-date_joined")[:10]
        ctx["recent_histories"] = DeviceHistory.objects.select_related('performed_by', 'device').all()[:100]
        return ctx


class PendingUserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "accounts/pending_user_list.html"
    context_object_name = "users"
    paginate_by = 50

    def get_queryset(self):
        return (
            User.objects.filter(is_approved=False)
            .exclude(role=User.Role.ADMIN)
            .order_by("-date_joined")
        )


class ApproveUserView(AdminRequiredMixin, View):
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            messages.error(request, "Người dùng không tồn tại.")
            return redirect("accounts:admin_dashboard")
        user.is_approved = True
        user.is_active = True
        user.is_rejected = False
        user.save()
        messages.success(request, f"Đã duyệt tài khoản {user.username}.")
        return redirect("accounts:admin_dashboard")


class RejectUserView(AdminRequiredMixin, View):
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            messages.error(request, "Người dùng không tồn tại.")
            return redirect("accounts:admin_dashboard")
        user.is_active = False
        user.is_approved = False
        user.is_rejected = True
        user.save()
        messages.success(request, f"Đã từ chối tài khoản {user.username}.")
        return redirect("accounts:admin_dashboard")


class UserActionView(AdminRequiredMixin, View):
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            messages.error(request, "Người dùng không tồn tại.")
            return redirect("accounts:admin_dashboard")

        action = request.POST.get("action")
        if action == "approve":
            user.is_approved = True
            user.is_active = True
            user.is_rejected = False
            user.save()
            messages.success(request, f"Đã duyệt tài khoản {user.username}.")
        elif action == "reject":
            user.is_active = False
            user.is_approved = False
            user.is_rejected = True
            user.save()
            messages.success(request, f"Đã từ chối tài khoản {user.username}.")
        else:
            messages.error(request, "Hành động không hợp lệ.")

        return redirect("accounts:admin_dashboard")


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


class RegisterStatusView(TemplateView):
    template_name = "accounts/register_status.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user_id = self.request.session.get("registered_user_id")
        user = None
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                user = None
        ctx["registered_user"] = user
        return ctx
