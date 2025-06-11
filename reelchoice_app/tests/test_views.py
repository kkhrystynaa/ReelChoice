from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('reelchoice_app:home')
        self.signup_url = reverse('reelchoice_app:authView')
        self.login_url = reverse('reelchoice_app:login')

    def test_home_view_redirects_if_not_logged_in(self):
        response = self.client.get(self.home_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.home_url}')

    def test_home_view_loads_if_logged_in(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_auth_view_get(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')
        self.assertIsInstance(response.context['form'], UserCreationForm)

    def test_ratings_view_accessible_from_home(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        ratings_url = reverse('reelchoice_app:ratings')
        response = self.client.get(ratings_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ratings.html') 

    def test_search_view_accessible_from_home(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        search_url = reverse('reelchoice_app:search')
        response = self.client.get(search_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_results.html') 

