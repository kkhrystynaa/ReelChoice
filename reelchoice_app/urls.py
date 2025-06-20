from django.urls import path, include

from . import views
from .views import authView, home
from django.contrib.auth.views import LoginView

urlpatterns = [
    # Home page URL - root URL mapped to the home view
    path("", home, name="home"),

    # Signup page URL mapped to the authView view
    path("signup/", authView, name="authView"),

    # Login page URL using Django's built-in LoginView with a custom template
    path("login/", LoginView.as_view(template_name="registration/login.html"), name="login"),

    # Include Django's built-in authentication URL patterns
    path("accounts/", include("django.contrib.auth.urls")),

    # Search movies page URL mapped to the search_movies view
    path("search/", views.search_movies, name="search"),

    # Ratings page URL mapped to the ratings_view view
    path('ratings/', views.ratings_view, name='ratings'),

    # Movie details page URL mapped to the movie_details_view view
    path("movie/", views.movie_details_view, name="movie"),

    # Category page URL, accepts a string parameter 'title', mapped to category_view
    path("category/<str:title>/", views.category_view, name="category_view"),

    # Detailed movie page URL, accepts an integer movie_id parameter, mapped to movie_details_view
    path("movie/<int:movie_id>/", views.movie_details_view, name="movie_detail")
]
