from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for the QR Device Management System.

    Extends Django's ``AbstractUser`` so we can add project-specific fields and
    role-based access control (RBAC) without painful migrations later.

    A simple ``role`` choices field is provided now for early-stage RBAC. In
    Phase 3 this can be complemented by a dedicated ``Role`` model (FK) if more
    granular, data-driven permissions are required.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        TECHNICIAN = "technician", "Technician"
        VIEWER = "viewer", "Viewer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text="Role used for access control.",
    )
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    employee_code = models.CharField(
        max_length=20, unique=True, blank=True, null=True, verbose_name="Mã nhân viên"
    )
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        name = self.get_full_name() or self.username
        if self.employee_code:
            return f"[{self.employee_code}] {name}"
        return name

    def save(self, *args, **kwargs):
        if not self.employee_code:
            users = User.objects.filter(employee_code__iregex=r'^u\d+$')
            max_num = 0
            for u in users:
                try:
                    num = int(u.employee_code.lower().replace('u', ''))
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
            self.employee_code = f"u{max_num + 1:02d}"
        super().save(*args, **kwargs)

    # --- RBAC convenience helpers -------------------------------------------
    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

    @property
    def is_manager(self) -> bool:
        return self.role == self.Role.MANAGER

    @property
    def is_technician(self) -> bool:
        return self.role == self.Role.TECHNICIAN

    @property
    def is_staff_role(self) -> bool:
        """Admin, Manager or Technician (i.e. can create/edit devices)."""
        return self.is_superuser or self.role in (
            self.Role.ADMIN,
            self.Role.MANAGER,
            self.Role.TECHNICIAN,
        )

    @property
    def is_manager_role(self) -> bool:
        """Admin or Manager (i.e. can delete / manage taxonomy)."""
        return self.is_superuser or self.role in (
            self.Role.ADMIN,
            self.Role.MANAGER,
        )
