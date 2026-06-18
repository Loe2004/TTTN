import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse


class TimeStampedModel(models.Model):
    """Abstract base adding created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    """A device category (e.g. Laptop, Printer, Router)."""

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Location(TimeStampedModel):
    """A physical location (building / room / department)."""

    name = models.CharField(max_length=150)
    building = models.CharField(max_length=120, blank=True)
    room = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ("name",)

    def __str__(self) -> str:
        parts = [self.name]
        if self.room:
            parts.append(self.room)
        return " - ".join(parts)


class Device(TimeStampedModel):
    """A managed physical device, identified by a UUID encoded in its QR code."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Hoạt động"
        MAINTENANCE = "maintenance", "Đang bảo trì"
        BROKEN = "broken", "Hỏng / Thanh lý"

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    name = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=120, blank=True)
    model = models.CharField(max_length=120, blank=True)
    manufacturer = models.CharField(max_length=120, blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_devices",
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)

    image = models.ImageField(upload_to="devices/", blank=True, null=True)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("devices:device_detail", kwargs={"pk": self.pk})

    @property
    def status_badge_class(self) -> str:
        """Map status to a design-system badge modifier."""
        return {
            self.Status.ACTIVE: "badge--success",
            self.Status.MAINTENANCE: "badge--warning",
            self.Status.BROKEN: "badge--danger",
        }.get(self.status, "badge--muted")

    @property
    def assigned_to_display(self) -> str:
        """Safely return full name, username, or placeholder."""
        if self.assigned_to:
            return self.assigned_to.get_full_name() or self.assigned_to.username
        return "—"


class MaintenanceLog(TimeStampedModel):
    """A maintenance / repair record for a device."""

    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="maintenance_logs"
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="maintenance_logs",
    )
    action = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, blank=True
    )
    performed_at = models.DateTimeField()

    class Meta:
        verbose_name = "Maintenance Log"
        verbose_name_plural = "Maintenance Logs"
        ordering = ("-performed_at",)

    def __str__(self) -> str:
        return f"{self.device.name} — {self.action}"
