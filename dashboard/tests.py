from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class AdminPanelAccessTests(TestCase):
    def test_anonymous_redirected(self):
        resp = self.client.get(reverse("admin_panel"))
        self.assertEqual(resp.status_code, 302)

    def test_student_forbidden(self):
        self.client.force_login(CustomUser.objects.create_user("stu", password="pass12345!"))
        self.assertEqual(self.client.get(reverse("admin_panel")).status_code, 403)

    def test_admin_allowed(self):
        self.client.force_login(CustomUser.objects.create_user("boss", password="pass12345!", role="ADMIN"))
        self.assertEqual(self.client.get(reverse("admin_panel")).status_code, 200)


class DashboardTests(TestCase):
    def test_dashboard_requires_login(self):
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 302)

    def test_dashboard_renders(self):
        self.client.force_login(CustomUser.objects.create_user("stu", password="pass12345!"))
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)


class DashboardCompletenessTests(TestCase):
    def test_incomplete_profile_shows_partial_gauge(self):
        user = CustomUser.objects.create_user("stu", password="pass12345!", first_name="Stu")
        self.client.force_login(user)
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.context["filled"], 1)
        self.assertEqual(resp.context["completeness"], 25)
        self.assertFalse(resp.context["profile_complete"])
        self.assertContains(resp, "Complete Profile")

    def test_complete_profile_shows_full_gauge(self):
        user = CustomUser.objects.create_user(
            "stu", "s@x.com", "pass12345!", first_name="Stu", last_name="Dent", course="BSCS")
        self.client.force_login(user)
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.context["completeness"], 100)
        self.assertNotContains(resp, "Complete Profile")
