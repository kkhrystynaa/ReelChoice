from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class TestNavigation(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('reelchoice_app:authView')
        self.login_url = reverse('reelchoice_app:login')
        self.logout_url = reverse('reelchoice_app:logout')
        self.home_url = reverse('reelchoice_app:home')

        self.credentials = {
            'username': 'username',
            'password': 'correct_password'
        }
        User.objects.create_user(**self.credentials)

    def test_signup_page_accessible(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_login_redirects_to_home(self):
        response = self.client.post(self.login_url, self.credentials, follow=True)
        self.assertRedirects(response, self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_requires_login(self):
        response = self.client.get(self.home_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.home_url}")

    def test_home_access_after_login(self):
        self.client.login(**self.credentials)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_logout_redirects_to_login(self):
        self.client.login(**self.credentials)
        response = self.client.post(self.logout_url, follow=True)
        self.assertRedirects(response, self.login_url)
        self.assertContains(response, "<h3>Login", html=True) 

