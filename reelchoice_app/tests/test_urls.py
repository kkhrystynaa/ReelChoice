from django.test import SimpleTestCase
from django.urls import reverse, resolve
from reelchoice_app.views import home, authView
from django.contrib.auth.views import LoginView
from reelchoice_app import views

class TestUrls(SimpleTestCase):
    # Test that the 'home' URL resolves to the correct view function
    def test_home_url_is_resolved(self):
        url = reverse("reelchoice_app:home")
        self.assertEqual(resolve(url).func, home)

    # Test that the 'signup' URL resolves to the authView function
    def test_signup_url_is_resolved(self):
        url = reverse("reelchoice_app:authView")
        self.assertEqual(resolve(url).func, authView)

    # Test that the 'login' URL resolves to Django's built-in LoginView class-based view
    def test_login_url_is_resolved(self):
        url = reverse("reelchoice_app:login")
        self.assertEqual(resolve(url).func.view_class, LoginView)
        
    # Test that the login view uses the correct template
    def test_login_template_used(self):
        response = self.client.get(reverse("reelchoice_app:login"))
        self.assertTemplateUsed(response, "registration/login.html")

    # Test that the 'search' URL resolves to the search_movies view function
    def test_search_url_is_resolved(self):
        url = reverse("reelchoice_app:search")
        self.assertEqual(resolve(url).func, views.search_movies)

    # Test that the 'ratings' URL resolves to the ratings_view function
    def test_ratings_url_is_resolved(self):
        url = reverse("reelchoice_app:ratings")
        self.assertEqual(resolve(url).func, views.ratings_view)

    # Test that the 'movie' URL resolves to the movie_details_view function
    def test_movie_url_is_resolved(self):
        url = reverse("reelchoice_app:movie")
        self.assertEqual(resolve(url).func, views.movie_details_view)

    # Test that the URL with movie ID parameter resolves to movie_details_view function
    def test_movie_id_url_is_resolved(self):
        url = reverse("reelchoice_app:movie_detail", args=(5,))
        self.assertEqual(resolve(url).func, views.movie_details_view)

    # Test that the category URL with a title parameter resolves to category_view function
    def test_category_title_url_is_resolved(self):
        url = reverse("reelchoice_app:category_view", args=("Viewers' Choice",))
        self.assertEqual(resolve(url).func, views.category_view)
