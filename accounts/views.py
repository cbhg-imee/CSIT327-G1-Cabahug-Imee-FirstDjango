from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import CustomUserCreationForm, ProfileUpdateForm
from .models import CustomUser


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Sign-up successful! Account '{self.object.username}' is online. You can now log in.",
        )
        return response


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Lets a logged-in user view/update THEIR OWN profile only.

    IDOR protection is layered:
      1. LoginRequiredMixin   -> anonymous users are redirected to the login page.
      2. UserPassesTestMixin  -> compares the pk in the URL with request.user.pk
                                 *before* any database lookup, so another user's
                                 profile returns 403 whether or not it exists
                                 (no user enumeration through 403-vs-404).
      3. get_object() override -> defense in depth; re-checks ownership on the
                                 fetched object.
    """

    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = "accounts/profile.html"

    def test_func(self):
        return self.kwargs.get(self.pk_url_kwarg) == self.request.user.pk

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.pk != self.request.user.pk:
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Profile updated. Changes saved to the panel.")
        return response

    def get_success_url(self):
        return reverse("profile", kwargs={"pk": self.object.pk})
