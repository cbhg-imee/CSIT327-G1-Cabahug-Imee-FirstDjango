from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import CustomAuthenticationForm
from .views import ProfileUpdateView, SignUpView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    # Declared before django.contrib.auth.urls (see campusconnect/urls.py) so
    # this styled login form takes precedence over the default one.
    path(
        "login/",
        auth_views.LoginView.as_view(authentication_form=CustomAuthenticationForm),
        name="login",
    ),
    path("profile/<int:pk>/", ProfileUpdateView.as_view(), name="profile"),
]
