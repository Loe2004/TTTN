"""Forms for authentication and user management.

All form widgets get the ``form-control`` CSS class so they match the design
system defined in ``frontend_guidelines.md``.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)

User = get_user_model()

ROLE_CHOICES = [
    (User.Role.MANAGER, "Manager"),
    (User.Role.TECHNICIAN, "Technician"),
    (User.Role.VIEWER, "Viewer"),
]


class StyledFormMixin:
    """Add the ``form-control`` class (and placeholders) to every field widget."""

    def _style_fields(self):
        for field in self.fields.values():
            widget = field.widget
            css = widget.attrs.get("class", "")
            if not isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                widget.attrs["class"] = (css + " form-control").strip()
            if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.PasswordInput)):
                widget.attrs.setdefault("placeholder", field.label or "")


class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Tên đăng nhập"
        self.fields["password"].widget.attrs["placeholder"] = "Mật khẩu"
        self._style_fields()


class RegisterForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=True, max_length=30, label="Họ")
    last_name = forms.CharField(required=True, max_length=30, label="Tên")
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Vai trò", initial=User.Role.VIEWER)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Tên đăng nhập"
        self.fields["first_name"].widget.attrs["placeholder"] = "Họ"
        self.fields["last_name"].widget.attrs["placeholder"] = "Tên"
        self.fields["email"].widget.attrs["placeholder"] = "Email"
        self.fields["password1"].widget.attrs["placeholder"] = "Mật khẩu"
        self.fields["password2"].widget.attrs["placeholder"] = "Xác nhận mật khẩu"
        self._style_fields()

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng cho tài khoản khác.")
        return email


class UserCreateForm(StyledFormMixin, UserCreationForm):
    """Admin form for creating a new user (replaces public registration)."""

    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Vai trò")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
        )
        labels = {
            "username": "Tên đăng nhập",
            "first_name": "Họ",
            "last_name": "Tên",
            "email": "Email",
            "role": "Vai trò",
            "is_active": "Trạng thái hoạt động",
        }
        help_texts = {
            "username": "Bắt buộc. 150 ký tự trở xuống. Chỉ chứa chữ cái, số và @/./+/-/_.",
            "is_active": "Chỉ định xem tài khoản có được phép đăng nhập hay không.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = ROLE_CHOICES
        self.fields["role"].initial = User.Role.VIEWER
        if "password1" in self.fields:
            self.fields["password1"].label = "Mật khẩu"
            self.fields["password1"].help_text = ""
        if "password2" in self.fields:
            self.fields["password2"].label = "Xác nhận mật khẩu"
            self.fields["password2"].help_text = "Nhập lại mật khẩu để xác nhận."
        self._style_fields()


class UserUpdateForm(StyledFormMixin, forms.ModelForm):
    """Admin form for editing an existing user (without changing password)."""

    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Vai trò")

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "avatar",
            "is_active",
        )
        labels = {
            "username": "Tên đăng nhập",
            "first_name": "Họ",
            "last_name": "Tên",
            "email": "Email",
            "role": "Vai trò",
            "avatar": "Ảnh đại diện",
            "is_active": "Trạng thái hoạt động",
        }
        help_texts = {
            "username": "Bắt buộc. 150 ký tự trở xuống. Chỉ chứa chữ cái, số và @/./+/-/_.",
            "is_active": "Chỉ định xem tài khoản có được phép đăng nhập hay không.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class ProfileForm(StyledFormMixin, forms.ModelForm):
    """Form for a user to edit their own profile."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "avatar")
        labels = {
            "first_name": "Họ",
            "last_name": "Tên",
            "email": "Email",
            "avatar": "Ảnh đại diện",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()

class AdminProfileForm(ProfileForm):
    class Meta(ProfileForm.Meta):
        fields = ("first_name", "last_name", "email", "role", "avatar")
        labels = {
            **ProfileForm.Meta.labels,
            "role": "Vai trò (Dành riêng cho Admin linh hoạt chuyển đổi)",
        }


class StyledPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "old_password" in self.fields:
            self.fields["old_password"].label = "Mật khẩu cũ"
        if "new_password1" in self.fields:
            self.fields["new_password1"].label = "Mật khẩu mới"
            self.fields["new_password1"].help_text = "Mật khẩu phải chứa ít nhất 8 ký tự và không được quá giống với thông tin cá nhân."
        if "new_password2" in self.fields:
            self.fields["new_password2"].label = "Xác nhận mật khẩu mới"
            self.fields["new_password2"].help_text = "Nhập lại mật khẩu mới để xác nhận."
        self._style_fields()


class StyledPasswordResetForm(StyledFormMixin, PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "email" in self.fields:
            self.fields["email"].label = "Địa chỉ Email"
            self.fields["email"].widget.attrs["placeholder"] = "Nhập email của bạn"
        self._style_fields()


class StyledSetPasswordForm(StyledFormMixin, SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "new_password1" in self.fields:
            self.fields["new_password1"].label = "Mật khẩu mới"
            self.fields["new_password1"].help_text = "Mật khẩu phải chứa ít nhất 8 ký tự và không được quá giống với thông tin cá nhân."
        if "new_password2" in self.fields:
            self.fields["new_password2"].label = "Xác nhận mật khẩu mới"
            self.fields["new_password2"].help_text = "Nhập lại mật khẩu mới để xác nhận."
        self._style_fields()
