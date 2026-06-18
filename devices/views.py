"""Views for the devices app.

- Device / Category / Location CRUD (RBAC-protected).
- Maintenance logs attached to a device.
- QR code auto-generation on device create, plus a printable label page.
- A camera-based QR scanner page and a JSON API to resolve a UUID to a device.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from accounts.mixins import ManagerRequiredMixin, StaffRequiredMixin

from .forms import CategoryForm, DeviceForm, LocationForm, MaintenanceLogForm
from .models import Category, Device, Location, MaintenanceLog
from .utils import assign_qr_code


# ---------------------------------------------------------------------------
# Devices CRUD
# ---------------------------------------------------------------------------
class DeviceListView(LoginRequiredMixin, ListView):
    model = Device
    template_name = "devices/device_list.html"
    context_object_name = "devices"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("category", "location", "assigned_to")
        )
        params = self.request.GET
        search = params.get("q", "").strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(serial_number__icontains=search)
                | Q(model__icontains=search)
                | Q(manufacturer__icontains=search)
            )
        if params.get("status"):
            qs = qs.filter(status=params["status"])
        if params.get("category"):
            qs = qs.filter(category_id=params["category"])
        if params.get("location"):
            qs = qs.filter(location_id=params["location"])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = Device.Status.choices
        ctx["categories"] = Category.objects.all()
        ctx["locations"] = Location.objects.all()
        ctx["current"] = {
            "q": self.request.GET.get("q", ""),
            "status": self.request.GET.get("status", ""),
            "category": self.request.GET.get("category", ""),
            "location": self.request.GET.get("location", ""),
        }
        return ctx


class DeviceDetailView(LoginRequiredMixin, DetailView):
    model = Device
    template_name = "devices/device_detail.html"
    context_object_name = "device"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["logs"] = self.object.maintenance_logs.select_related("performed_by")
        ctx["log_form"] = MaintenanceLogForm()
        return ctx


class DeviceCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Device
    form_class = DeviceForm
    template_name = "devices/device_form.html"
    success_message = "Đã thêm thiết bị."

    def form_valid(self, form):
        response = super().form_valid(form)
        # Generate and store the QR code (uploaded to Cloudinary).
        assign_qr_code(self.object, request=self.request)
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Thêm thiết bị"
        return ctx


class DeviceUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Device
    form_class = DeviceForm
    template_name = "devices/device_form.html"
    success_message = "Đã cập nhật thiết bị."

    def form_valid(self, form):
        response = super().form_valid(form)
        if not self.object.qr_code:
            assign_qr_code(self.object, request=self.request)
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Sửa thiết bị"
        return ctx


class DeviceDeleteView(ManagerRequiredMixin, DeleteView):
    model = Device
    template_name = "devices/device_confirm_delete.html"
    success_url = reverse_lazy("devices:device_list")

    def form_valid(self, form):
        # Soft delete: just set is_active to False
        self.object.is_active = False
        self.object.save()
        messages.success(self.request, "Đã khóa thiết bị.")
        return redirect(self.success_url)


class DeviceBulkDeactivateView(ManagerRequiredMixin, View):
    """Deactivate multiple devices at once."""

    def post(self, request):
        ids = request.POST.get("ids", "").split(",")
        valid_ids = [i for i in ids if i.isdigit()]
        if valid_ids:
            count = Device.objects.filter(id__in=valid_ids).update(is_active=False)
            messages.success(request, f"Đã khóa {count} thiết bị.")
        return redirect("devices:device_list")


# ---------------------------------------------------------------------------
# Maintenance logs
# ---------------------------------------------------------------------------
class MaintenanceLogCreateView(StaffRequiredMixin, View):
    """Add a maintenance log to a device (posted from the detail page)."""

    def post(self, request, device_pk):
        device = get_object_or_404(Device, pk=device_pk)
        form = MaintenanceLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.device = device
            log.performed_by = request.user
            log.save()
            messages.success(request, "Đã thêm nhật ký bảo trì.")
        else:
            messages.error(request, "Dữ liệu nhật ký không hợp lệ.")
        return redirect("devices:device_detail", pk=device_pk)


# ---------------------------------------------------------------------------
# Category CRUD
# ---------------------------------------------------------------------------
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "devices/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(ManagerRequiredMixin, SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "devices/simple_form.html"
    success_url = reverse_lazy("devices:category_list")
    success_message = "Đã thêm danh mục."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Thêm danh mục"
        ctx["back_url"] = reverse_lazy("devices:category_list")
        return ctx


class CategoryUpdateView(ManagerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "devices/simple_form.html"
    success_url = reverse_lazy("devices:category_list")
    success_message = "Đã cập nhật danh mục."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Sửa danh mục"
        ctx["back_url"] = reverse_lazy("devices:category_list")
        return ctx


class CategoryDeleteView(ManagerRequiredMixin, DeleteView):
    model = Category
    template_name = "devices/confirm_delete.html"
    success_url = reverse_lazy("devices:category_list")

    def form_valid(self, form):
        self.object.is_active = False
        self.object.save()
        messages.success(self.request, "Đã khóa danh mục.")
        return redirect(self.success_url)


class CategoryBulkDeactivateView(ManagerRequiredMixin, View):
    def post(self, request):
        ids = request.POST.get("ids", "").split(",")
        valid_ids = [i for i in ids if i.isdigit()]
        if valid_ids:
            count = Category.objects.filter(id__in=valid_ids).update(is_active=False)
            messages.success(request, f"Đã khóa {count} danh mục.")
        return redirect("devices:category_list")


# ---------------------------------------------------------------------------
# Location CRUD
# ---------------------------------------------------------------------------
class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = "devices/location_list.html"
    context_object_name = "locations"


class LocationCreateView(ManagerRequiredMixin, SuccessMessageMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = "devices/simple_form.html"
    success_url = reverse_lazy("devices:location_list")
    success_message = "Đã thêm vị trí."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Thêm vị trí"
        ctx["back_url"] = reverse_lazy("devices:location_list")
        return ctx


class LocationUpdateView(ManagerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = "devices/simple_form.html"
    success_url = reverse_lazy("devices:location_list")
    success_message = "Đã cập nhật vị trí."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Sửa vị trí"
        ctx["back_url"] = reverse_lazy("devices:location_list")
        return ctx


class LocationDeleteView(ManagerRequiredMixin, DeleteView):
    model = Location
    template_name = "devices/confirm_delete.html"
    success_url = reverse_lazy("devices:location_list")

    def form_valid(self, form):
        self.object.is_active = False
        self.object.save()
        messages.success(self.request, "Đã khóa vị trí.")
        return redirect(self.success_url)


class LocationBulkDeactivateView(ManagerRequiredMixin, View):
    def post(self, request):
        ids = request.POST.get("ids", "").split(",")
        valid_ids = [i for i in ids if i.isdigit()]
        if valid_ids:
            count = Location.objects.filter(id__in=valid_ids).update(is_active=False)
            messages.success(request, f"Đã khóa {count} vị trí.")
        return redirect("devices:location_list")


# ---------------------------------------------------------------------------
# QR Code system (Phase 5)
# ---------------------------------------------------------------------------
class DeviceQRView(LoginRequiredMixin, DetailView):
    """Printable QR label page for a device."""

    model = Device
    template_name = "devices/device_qr.html"
    context_object_name = "device"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Lazily generate a QR code if one is missing.
        if not self.object.qr_code:
            assign_qr_code(self.object, request=request)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class BulkDeviceQRView(LoginRequiredMixin, ListView):
    """Printable QR label page for multiple devices."""

    model = Device
    template_name = "devices/bulk_qr.html"
    context_object_name = "devices"

    def get_queryset(self):
        ids = self.request.GET.get("ids", "").split(",")
        # Filter out empty strings and non-digit strings
        valid_ids = [i for i in ids if i.isdigit()]
        if not valid_ids:
            return Device.objects.none()

        qs = Device.objects.filter(id__in=valid_ids)

        # Ensure all selected devices have a QR code
        for device in qs:
            if not device.qr_code:
                assign_qr_code(device, request=self.request)

        return qs


class ScannerView(LoginRequiredMixin, TemplateView):
    """Camera-based QR scanner page (uses html5-qrcode)."""

    template_name = "devices/scanner.html"


class DeviceResolveAPIView(LoginRequiredMixin, View):
    """Resolve a scanned UUID to device info (JSON)."""

    def get(self, request, uuid):
        try:
            device = Device.objects.select_related(
                "category", "location", "assigned_to"
            ).get(uuid=uuid)
        except Device.DoesNotExist:
            return JsonResponse(
                {"found": False, "message": "Không tìm thấy thiết bị."}, status=404
            )

        if not device.is_active:
            return JsonResponse(
                {"found": False, "message": "Thiết bị này đã bị khóa."}, status=403
            )

        return JsonResponse(
            {
                "found": True,
                "device": {
                    "name": device.name,
                    "serial_number": device.serial_number,
                    "status": device.get_status_display(),
                    "category": device.category.name if device.category else None,
                    "location": str(device.location) if device.location else None,
                    "assigned_to": device.assigned_to_display,
                    "detail_url": device.get_absolute_url(),
                },
            }
        )
