import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from .models import Movie
from .services import search_movies_by_title, get_user_ratings_data


@login_required
def home(request):
    user = request.user

    # Viewers' Choice
    top_movies = Movie.objects.order_by('-vote_average')[:50]
    viewers_choice = random.sample(list(top_movies.values('title', 'poster_path', 'vote_average')), 5)

    # Recommended for you
    all_ids = list(Movie.objects.values_list('id', flat=True))
    recommended_ids = random.sample(all_ids, min(5, len(all_ids)))
    recommended = Movie.objects.filter(id__in=recommended_ids).values('title', 'poster_path', 'vote_average')

    # True Story
    true_story_qs = Movie.objects.filter(overview__icontains='true story')
    true_story = random.sample(list(true_story_qs.values('title', 'poster_path', 'vote_average')),
                               min(5, true_story_qs.count()))

    # Horror
    horror_qs = Movie.objects.filter(genres__name__iexact='Horror')
    horror = random.sample(list(horror_qs.values('title', 'poster_path', 'vote_average')), min(5, horror_qs.count()))

    # Rate More Movies
    if user.is_authenticated:
        rated_ids = user.ratings.values_list('movie_id', flat=True)
        unrated_qs = Movie.objects.exclude(id__in=rated_ids)
    else:
        unrated_qs = Movie.objects.all()

    unrated = random.sample(list(unrated_qs.values('title', 'poster_path', 'vote_average')), min(5, unrated_qs.count()))

    sections = [
        {"title": "Viewers' Choice", "movies": viewers_choice},
        {"title": "Recommended for you", "movies": recommended},
        {"title": "Based on a true story", "movies": true_story},
        {"title": "Top Horror Movies", "movies": horror},
        {"title": "Rate More Movies", "movies": unrated},
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

    # mock data for testing
    if True:
        test_qs = Movie.objects.all()
        movies = random.sample(list(test_qs.values('title', 'poster_path')), min(10, test_qs.count()))
        ratings = [
            {
                'title': r["title"],
                'poster_path': r["poster_path"],
                'score': random.choice([4.0, 4.5, 5.0])
            }
            for r in movies
        ]
    return render(request, 'ratings.html', {'ratings': ratings})


def movie_details_view(request):
    # mock data for testing
    movie = Movie.objects.first()
    movie_data = Movie.objects.filter(id=movie.id).values().first()
    return render(request, "movie_detail.html", {"movie": movie_data})