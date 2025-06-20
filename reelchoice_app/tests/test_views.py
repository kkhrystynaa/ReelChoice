from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from reelchoice_app.models import Movie


class TestViews(TestCase):

    def setUp(self):
        # Initialize test client and URLs for reuse in tests
        self.client = Client()
        self.signup_url = reverse('reelchoice_app:authView')
        self.login_url = reverse('reelchoice_app:login')
        self.logout_url = reverse('reelchoice_app:logout')
        self.home_url = reverse('reelchoice_app:home')
        self.search_url = reverse('reelchoice_app:search')
        self.ratings_url = reverse('reelchoice_app:ratings')
        self.movie_url = reverse('reelchoice_app:movie_detail', args=(1,))
        self.category_url = reverse('reelchoice_app:category_view', args=("Viewers' Choice",))

        # Create test user credentials and user object
        self.credentials = {
            'username': 'username',
            'password': 'correct_password'
        }
        self.user = User.objects.create_user(**self.credentials)

        # Create a sample Movie object for testing movie-related views
        self.movie1 = Movie.objects.create(
            id=1,
            title="Inception",
            poster_path="/inception.jpg",
            runtime=148,
            vote_average=8.8,
            overview="Dreams within dreams."
        )

    # Test that home view redirects to login page when user is not authenticated
    def test_home_view_redirects_if_not_logged_in(self):
        response = self.client.get(self.home_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.home_url}')

    # Test that home view loads successfully for authenticated users
    def test_home_view_loads_if_logged_in(self):
        self.client.login(**self.credentials)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    # Test GET request on signup page returns status 200 and uses the signup template
    # Also verifies the context contains a UserCreationForm instance
    def test_auth_view_get(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')
        self.assertIsInstance(response.context['form'], UserCreationForm)

    # Test signup page is accessible and uses correct template
    def test_signup_page_accessible(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

    # Test successful login redirects to the home page with correct status and template
    def test_login_redirects_to_home(self):
        response = self.client.post(self.login_url, self.credentials, follow=True)
        self.assertRedirects(response, self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    # Test logout redirects to login page and login page contains expected HTML content
    def test_logout_redirects_to_login(self):
        self.client.login(**self.credentials)
        response = self.client.post(self.logout_url, follow=True)
        self.assertRedirects(response, self.login_url)
        self.assertContains(response, "<h2 class=\"text-[24px] font-semibold mb-4\">Login</h2>", html=True)

    # Test that ratings view is accessible and uses correct template after login
    def test_ratings_view_accessible_after_login(self):
        self.client.login(**self.credentials)
        response = self.client.get(self.ratings_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ratings.html')

    # Test that search view is accessible and uses correct template after login
    def test_search_view_accessible_after_login(self):
        self.client.login(**self.credentials)
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_results.html') 

    # Test that movie detail view is accessible and uses correct template after login
    def test_movie_view_accessible_after_login(self):
        self.client.login(**self.credentials)
        response = self.client.get(self.movie_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie_detail.html')

    # Test that category detail view is accessible and uses correct template after login
    def test_category_view_accessible_after_login(self):
        self.client.login(**self.credentials)
        response = self.client.get(self.category_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'category_detail.html')
