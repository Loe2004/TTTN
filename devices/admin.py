from django.contrib import admin

from .models import Category, Device, Location, MaintenanceLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "building", "room", "created_at")
    search_fields = ("name", "building", "room")


class MaintenanceLogInline(admin.TabularInline):
    model = MaintenanceLog
    extra = 0


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "serial_number",
        "category",
        "location",
        "status",
        "assigned_to",
        "created_at",
    )
    list_filter = ("status", "category", "location")
    search_fields = ("name", "serial_number", "model", "manufacturer", "uuid")
    readonly_fields = ("uuid", "qr_code", "created_at", "updated_at")
    inlines = [MaintenanceLogInline]


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ("device", "action", "performed_by", "cost", "performed_at")
    list_filter = ("performed_at",)
    search_fields = ("device__name", "action")
