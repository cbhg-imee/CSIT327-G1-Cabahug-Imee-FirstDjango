from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from .models import CustomUser


class ProfileAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = CustomUser.objects.create_user("alice", "alice@example.com", "pass12345!", first_name="Alice")
        cls.bob = CustomUser.objects.create_user("bob", "bob@example.com", "pass12345!", first_name="Bob")

    def url(self, user):
        return reverse("profile", kwargs={"pk": user.pk})

    def test_anonymous_redirected_to_login(self):
        resp = self.client.get(self.url(self.alice))
        self.assertRedirects(resp, f"{reverse('login')}?next={self.url(self.alice)}")

    def test_anonymous_cannot_post(self):
        self.client.post(self.url(self.alice), {"first_name": "Hacked"})
        self.alice.refresh_from_db()
        self.assertEqual(self.alice.first_name, "Alice")

    def test_owner_can_view_and_update(self):
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(self.url(self.alice)).status_code, 200)
        resp = self.client.post(self.url(self.alice), {
            "first_name": "Alicia", "last_name": "Cruz", "email": "a@new.com", "course": "BSCS",
        })
        self.assertRedirects(resp, self.url(self.alice))
        self.alice.refresh_from_db()
        self.assertEqual((self.alice.first_name, self.alice.course), ("Alicia", "BSCS"))

    def test_user_cannot_view_other_profile(self):
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(self.url(self.bob)).status_code, 403)

    def test_user_cannot_edit_other_profile(self):
        self.client.force_login(self.alice)
        resp = self.client.post(self.url(self.bob), {"first_name": "Pwned", "email": "x@x.com"})
        self.assertEqual(resp.status_code, 403)
        self.bob.refresh_from_db()
        self.assertEqual(self.bob.first_name, "Bob")

    def test_forbidden_page_is_themed(self):
        self.client.force_login(self.alice)
        resp = self.client.get(self.url(self.bob))
        self.assertTemplateUsed(resp, "403.html")
        self.assertContains(resp, "Access Denied", status_code=403)
        self.assertContains(resp, "bootstrap@5", status_code=403)

    def test_nonexistent_profile_is_indistinguishable_from_other_users(self):
        """403 (not 404) so attackers can't enumerate which user ids exist."""
        self.client.force_login(self.alice)
        resp = self.client.get(reverse("profile", kwargs={"pk": 99999}))
        self.assertEqual(resp.status_code, 403)

    def test_role_cannot_be_escalated_via_profile_post(self):
        self.client.force_login(self.alice)
        self.client.post(self.url(self.alice), {
            "first_name": "Alice", "email": "alice@example.com",
            "role": "ADMIN", "is_staff": "on", "is_superuser": "on",
        })
        self.alice.refresh_from_db()
        self.assertEqual(self.alice.role, CustomUser.Role.STUDENT)
        self.assertFalse(self.alice.is_staff or self.alice.is_superuser)


class SignUpTests(TestCase):
    data = {
        "username": "newbie", "email": "n@example.com", "first_name": "New", "last_name": "Bie",
        "course": "BSIT", "password1": "Str0ng-pass-987", "password2": "Str0ng-pass-987",
    }

    def test_signup_creates_user_and_flashes_success_message(self):
        resp = self.client.post(reverse("signup"), self.data, follow=True)
        self.assertRedirects(resp, reverse("login"))
        self.assertTrue(CustomUser.objects.filter(username="newbie").exists())
        msgs = list(get_messages(resp.wsgi_request))
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].tags, "success")
        # Rendered as a dismissible Bootstrap alert in base.html
        self.assertContains(resp, "alert alert-success alert-dismissible")
        self.assertContains(resp, 'data-bs-dismiss="alert"')

    def test_signup_ignores_role_field(self):
        self.client.post(reverse("signup"), {**self.data, "role": "ADMIN"})
        self.assertEqual(CustomUser.objects.get(username="newbie").role, CustomUser.Role.STUDENT)

    def test_invalid_signup_shows_no_success_message(self):
        resp = self.client.post(reverse("signup"), {**self.data, "password2": "mismatch"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(list(get_messages(resp.wsgi_request))), 0)


class TemplateTests(TestCase):
    def test_pages_extend_base_and_use_styled_forms(self):
        for name in ("login", "signup"):
            resp = self.client.get(reverse(name))
            self.assertTemplateUsed(resp, "base.html")
            self.assertContains(resp, "form-control")
            self.assertContains(resp, "csrfmiddlewaretoken")
            self.assertContains(resp, "bootstrap@5")
        self.client.force_login(CustomUser.objects.create_user("u", password="pass12345!"))
        resp = self.client.get(reverse("profile", kwargs={"pk": CustomUser.objects.get(username="u").pk}))
        self.assertTemplateUsed(resp, "base.html")
        self.assertContains(resp, "csrfmiddlewaretoken")


class ThemeTests(TestCase):
    def test_dark_mode_switch_present_for_everyone(self):
        resp = self.client.get(reverse("login"))
        self.assertContains(resp, 'id="themeToggle"')
        self.assertContains(resp, "cc-theme")  # preference is persisted

    def test_themed_404(self):
        resp = self.client.get("/definitely/not/a/page/")
        self.assertEqual(resp.status_code, 404)
        self.assertTemplateUsed(resp, "404.html")
