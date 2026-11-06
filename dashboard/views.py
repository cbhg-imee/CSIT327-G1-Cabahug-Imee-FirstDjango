from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView

from accounts.models import CustomUser


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member_count"] = CustomUser.objects.count()
        context["is_admin"] = self.request.user.role == CustomUser.Role.ADMIN

        
        user = self.request.user
        checklist = [
            {"label": "First name", "done": bool(user.first_name)},
            {"label": "Last name", "done": bool(user.last_name)},
            {"label": "Email address", "done": bool(user.email)},
            {"label": "Course", "done": bool(user.course)},
        ]
        filled = sum(item["done"] for item in checklist)
        context["checklist"] = checklist
        context["filled"] = filled
        context["total"] = len(checklist)
        context["completeness"] = round(filled / len(checklist) * 100)
        context["profile_complete"] = filled == len(checklist)
        return context


class AdminPanelView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Administrators only. Anonymous users are redirected to login;
    logged-in non-admins receive a 403."""

    template_name = "dashboard/admin_panel.html"

    def test_func(self):
        return self.request.user.role == CustomUser.Role.ADMIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["members"] = CustomUser.objects.order_by("last_name", "first_name", "username")
        return context
