
from django.urls import path, include

from . import views
from .views import authView, home
from django.contrib.auth.views import LoginView
urlpatterns = [
    path("", home, name="home"),
    path("signup/", authView, name="authView"),
    path("login/", LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("search/", views.search_movies, name="search"),
    path('ratings/', views.ratings_view, name='ratings'),
    path("category/<str:title>/", views.category_view, name="category_view"),
    path("movie/<int:movie_id>/", views.movie_details_view, name="movie_detail")
]
