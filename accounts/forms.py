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


class UserCreateForm(StyledFormMixin, UserCreationForm):
    """Admin form for creating a new user (replaces public registration)."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "phone",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class UserUpdateForm(StyledFormMixin, forms.ModelForm):
    """Admin form for editing an existing user (without changing password)."""

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "phone",
            "avatar",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class ProfileForm(StyledFormMixin, forms.ModelForm):
    """Form for a user to edit their own profile."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "avatar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class StyledPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class StyledPasswordResetForm(StyledFormMixin, PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class StyledSetPasswordForm(StyledFormMixin, SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()
