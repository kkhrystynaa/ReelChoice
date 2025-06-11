from django.test import SimpleTestCase
from django.urls import reverse, resolve
from reelchoice_app.views import home, authView
from django.contrib.auth.views import LoginView

class TestUrls(SimpleTestCase):
    def test_home_url_is_resolved(self):
        url = reverse("reelchoice_app:home")
        self.assertEqual(resolve(url).func, home)

    def test_signup_url_is_resolved(self):
        url = reverse("reelchoice_app:authView")
        self.assertEqual(resolve(url).func, authView)

    def test_login_url_is_resolved(self):
        url = reverse("reelchoice_app:login")
        self.assertEqual(resolve(url).func.view_class, LoginView)
        
    def test_login_template_used(self):
        response = self.client.get(reverse("reelchoice_app:login"))
        self.assertTemplateUsed(response, "registration/login.html")

