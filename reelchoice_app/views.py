from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .services import search_movies_by_title, get_user_ratings_data, get_movies_by_genre, get_movie_detail_info, \
    get_movie_comments
from .models import Genre, Movie


@login_required
def home(request):
    sections = [
        {
            "title": "Viewers' Choice",
            "movies": [
                {"title": "Inception", "poster_path": "/inception.jpg", "vote_average": 8.8},
                {"title": "The Dark Knight", "poster_path": "/darkknight.jpg", "vote_average": 9.0},
            ],
        },
        {
            "title": "Recommended for you",
            "movies": [
                {"title": "Interstellar", "poster_path": "/interstellar.jpg", "vote_average": 8.6},
                {"title": "Arrival", "poster_path": "/arrival.jpg", "vote_average": 7.9},
            ],
        },
        {
            "title": "Based on a true story",
            "movies": [
                {"title": "Catch Me If You Can", "poster_path": "/catchmeifyoucan.jpg", "vote_average": 8.1},
                {"title": "The Imitation Game", "poster_path": "/imitationgame.jpg", "vote_average": 8.0},
            ],
        },
        {
            "title": "Top Horror Movies",
            "movies": [
                {"title": "The Conjuring", "poster_path": "/conjuring.jpg", "vote_average": 7.5},
                {"title": "It", "poster_path": "/it.jpg", "vote_average": 7.3},
            ],
        },
        {
            "title": "Rate More Movies",
            "movies": [
                {"title": "Joker", "poster_path": "/joker.jpg", "vote_average": 8.5},
                {"title": "Parasite", "poster_path": "/parasite.jpg", "vote_average": 8.6},
            ],
        },
    ]
    return render(request, "home.html", {"sections": sections})


def authView(request):
 if request.method == "POST":
  form = UserCreationForm(request.POST or None)
  if form.is_valid():
   form.save()
   return redirect("reelchoice_app:login")
 else:
  form = UserCreationForm()
 return render(request, "registration/signup.html", {"form": form})


def search(request):
    query = request.GET.get("q", "")
    results = search_movies_by_title(query) if query else []
    return render(request, "search_results.html", {
        "query": query,
        "movies": results
    })


def ratings_view(request):
    ratings = get_user_ratings_data(request.user)
    return render(request, 'ratings.html', {'ratings': ratings})
