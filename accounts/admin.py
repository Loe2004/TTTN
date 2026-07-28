from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import redirect

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "is_staff",
        "is_active",
        "is_approved",
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "is_approved")
    actions = ("approve_users", "reject_users")
    search_fields = ("username", "email", "first_name", "last_name")
    # add per-row action buttons
    list_display = list(list_display) + ["approve_button", "reject_button"]

    # Extend the default fieldsets with our custom fields.
    fieldsets = BaseUserAdmin.fieldsets + (
        ("QR Device Manager", {"fields": ("role", "avatar")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("QR Device Manager", {"fields": ("role",)}),
    )

    @admin.action(description="Approve selected users")
    def approve_users(self, request, queryset):
        updated = queryset.update(is_approved=True, is_active=True, is_rejected=False)
        self.message_user(request, f"Đã duyệt {updated} tài khoản.")

    @admin.action(description="Reject (deactivate) selected users")
    def reject_users(self, request, queryset):
        updated = queryset.update(is_active=False, is_approved=False, is_rejected=True)
        self.message_user(request, f"Đã từ chối {updated} tài khoản.")

    # --- Per-row admin actions (buttons) ---------------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<int:user_id>/approve/", self.admin_site.admin_view(self.approve_user_view), name="accounts_user_approve"),
            path("<int:user_id>/reject/", self.admin_site.admin_view(self.reject_user_view), name="accounts_user_reject"),
        ]
        return custom_urls + urls

    def approve_user_view(self, request, user_id):
        if not self.has_change_permission(request):
            return redirect("..")
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return redirect("..")
        user.is_approved = True
        user.is_active = True
        user.is_rejected = False
        user.save()
        self.message_user(request, f"Đã duyệt tài khoản {user.username}.")
        return redirect(reverse("admin:accounts_user_changelist"))

    def reject_user_view(self, request, user_id):
        if not self.has_change_permission(request):
            return redirect("..")
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return redirect("..")
        user.is_active = False
        user.is_approved = False
        user.is_rejected = True
        user.save()
        self.message_user(request, f"Đã từ chối tài khoản {user.username}.")
        return redirect(reverse("admin:accounts_user_changelist"))

    def approve_button(self, obj):
        if obj.is_approved:
            return "—"
        url = reverse("admin:accounts_user_approve", args=[obj.pk])
        return format_html('<a class="button" href="{}">Duyệt</a>', url)

    approve_button.short_description = "Duyệt"

    def reject_button(self, obj):
        if obj.is_rejected:
            return "—"
        url = reverse("admin:accounts_user_reject", args=[obj.pk])
        return format_html('<a class="button button-danger" href="{}">Từ chối</a>', url)

    reject_button.short_description = "Từ chối"
