from django.test import SimpleTestCase
from django.urls import reverse, resolve
from reelchoice_app.views import home, authView
from django.contrib.auth.views import LoginView
from reelchoice_app import views

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

    def test_search_url_is_resolved(self):
        url = reverse("reelchoice_app:search")
        self.assertEqual(resolve(url).func, views.search_movies)

    def test_ratings_url_is_resolved(self):
        url = reverse("reelchoice_app:ratings")
        self.assertEqual(resolve(url).func, views.ratings_view)

    def test_movie_url_is_resolved(self):
        url = reverse("reelchoice_app:movie")
        self.assertEqual(resolve(url).func, views.movie_details_view)

    def test_movie_id_url_is_resolved(self):
        url = reverse("reelchoice_app:movie_detail", args=(5,))
        self.assertEqual(resolve(url).func, views.movie_details_view)

    def test_category_title_url_is_resolved(self):
        url = reverse("reelchoice_app:category_view", args=("Viewers' Choice",))
        self.assertEqual(resolve(url).func, views.category_view)
