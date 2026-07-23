"""Forms for the devices app, styled to match the design system."""

from django import forms

from .models import Category, Device, Location, MaintenanceLog


class StyledModelForm(forms.ModelForm):
    """Apply the ``form-control`` class to all widgets (design-system styling)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                continue
            css = widget.attrs.get("class", "")
            widget.attrs["class"] = (css + " form-control").strip()
            if isinstance(widget, (forms.DateInput,)):
                widget.input_type = "date"


class DeviceForm(StyledModelForm):
    class Meta:
        model = Device
        fields = (
            "name",
            "serial_number",
            "model",
            "manufacturer",
            "category",
            "location",
            "assigned_to",
            "status",
            "purchase_date",
            "warranty_expiry",
            "image",
            "notes",
        )
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "warranty_expiry": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "name": "Tên thiết bị",
            "serial_number": "Số Serial",
            "model": "Model (Mẫu mã)",
            "manufacturer": "Nhà sản xuất",
            "category": "Danh mục",
            "location": "Vị trí",
            "assigned_to": "Người phụ trách",
            "status": "Trạng thái",
            "purchase_date": "Ngày mua",
            "warranty_expiry": "Ngày hết hạn bảo hành",
            "image": "Hình ảnh",
            "notes": "Ghi chú",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.db.models import Q
        if self.instance and self.instance.pk:
            if self.instance.category_id:
                self.fields["category"].queryset = Category.objects.filter(
                    Q(is_active=True) | Q(id=self.instance.category_id)
                )
            else:
                self.fields["category"].queryset = Category.objects.filter(is_active=True)
                
            if self.instance.location_id:
                self.fields["location"].queryset = Location.objects.filter(
                    Q(is_active=True) | Q(id=self.instance.location_id)
                )
            else:
                self.fields["location"].queryset = Location.objects.filter(is_active=True)
        else:
            self.fields["category"].queryset = Category.objects.filter(is_active=True)
            self.fields["location"].queryset = Location.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        purchase_date = cleaned_data.get("purchase_date")
        warranty_expiry = cleaned_data.get("warranty_expiry")

        if purchase_date and warranty_expiry:
            if warranty_expiry < purchase_date:
                self.add_error(
                    "warranty_expiry", 
                    "Ngày hết hạn bảo hành không được nhỏ hơn ngày mua."
                )
        return cleaned_data


class CategoryForm(StyledModelForm):
    class Meta:
        model = Category
        fields = ("name", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
        labels = {
            "name": "Tên danh mục",
            "description": "Mô tả",
        }


class LocationForm(StyledModelForm):
    class Meta:
        model = Location
        fields = ("name", "building", "room", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
        labels = {
            "name": "Tên vị trí",
            "building": "Tòa nhà",
            "room": "Phòng",
            "description": "Mô tả",
        }


class MaintenanceLogForm(StyledModelForm):
    class Meta:
        model = MaintenanceLog
        fields = ("action", "notes", "cost", "performed_at")
        widgets = {
            "performed_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "action": "Hành động (Loại bảo trì)",
            "notes": "Chi tiết công việc / Ghi chú",
            "cost": "Chi phí (VNĐ)",
            "performed_at": "Thời gian thực hiện",
        }

    def __init__(self, *args, **kwargs):
        self.device = kwargs.pop("device", None)
        super().__init__(*args, **kwargs)
        self.fields["performed_at"].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean(self):
        cleaned_data = super().clean()
        performed_at = cleaned_data.get("performed_at")

        if performed_at and self.device and self.device.purchase_date:
            if performed_at.date() < self.device.purchase_date:
                self.add_error(
                    "performed_at",
                    f"Ngày bảo trì không được nhỏ hơn ngày mua thiết bị ({self.device.purchase_date.strftime('%d/%m/%Y')})."
                )
        return cleaned_data
