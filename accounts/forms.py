from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class BootstrapFormMixin:
    """Applies Bootstrap 5 form-control classes to every widget.

    Templates render each field manually (see templates/includes/form_field.html)
    so nothing is ever output with as_p / as_table.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            css = "form-check-input" if isinstance(widget, forms.CheckboxInput) else "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {css}".strip()
            widget.attrs.setdefault("placeholder", field.label or "")


class CustomAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    """Login form with Bootstrap-styled inputs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(autofocus=True, autocomplete="username")
        self.fields["password"].widget.attrs.update(autocomplete="current-password")


class CustomUserCreationForm(BootstrapFormMixin, UserCreationForm):
    """Sign-up form. `role` is intentionally NOT exposed: everyone registers as
    a student, and elevated roles can only be granted by an administrator."""

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "course")


class ProfileUpdateForm(BootstrapFormMixin, forms.ModelForm):
    """Profile edit form. Only harmless personal details are editable;
    `role`, `is_staff`, `is_superuser`, etc. are excluded to prevent
    privilege escalation through a crafted POST."""

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email", "course")
