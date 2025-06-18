import os
import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from ReelChoice import settings
from recommender.recommender import ItemBasedCF
from .forms import CommentForm
from .models import Movie, Rating
from .services import write_comment, rate_movie

MODEL_PATH = os.path.join(settings.BASE_DIR, 'recommender/trained_model.pkl')

item_based_model = ItemBasedCF()
item_based_model.load_model(MODEL_PATH)


@login_required
def home(request):
    user = request.user

    # Viewers' Choice
    top_movies = Movie.objects.all()
    viewers_choice = random.sample(list(top_movies), min(5, top_movies.count()))

    # Recommended for you (рекомендаційна система)
    user_ratings_qs = Rating.objects.filter(user=user)
    user_ratings = {r.movie_id: r.score for r in user_ratings_qs}
    recommendations = item_based_model.recommend_items(user_ratings, n_recommendations=20)
    recommended_ids_full = [movie_id for movie_id, _ in recommendations]

    if recommended_ids_full:
        recommended_ids = random.sample(recommended_ids_full, min(5, len(recommended_ids_full)))
    else:
        all_ids = list(Movie.objects.values_list('id', flat=True))
        recommended_ids = random.sample(all_ids, min(5, len(all_ids)))

    recommended = Movie.objects.filter(id__in=recommended_ids)

    # True Story
    true_story_qs = Movie.objects.filter(overview__icontains='true story')
    true_story = random.sample(list(true_story_qs), min(5, true_story_qs.count()))

    # Horror
    horror_qs = Movie.objects.filter(genres__name__iexact='Horror')
    horror = random.sample(list(horror_qs), min(5, horror_qs.count()))

    # Rate More Movies
    if user.is_authenticated:
        rated_ids = user.ratings.values_list('movie_id', flat=True)
        unrated_qs = Movie.objects.exclude(id__in=rated_ids)
    else:
        unrated_qs = Movie.objects.all()

    unrated = random.sample(list(unrated_qs), min(5, unrated_qs.count()))

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


def search_movies(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Movie.objects.filter(title__icontains=query)
    return render(request, 'search_results.html', {'query': query, 'movies': results})


def ratings_view(request):
    # Отримати всі рейтинги поточного користувача разом із відповідними фільмами
    ratings_qs = Rating.objects.select_related("movie").filter(user=request.user).order_by('-created_at')

    ratings = [
        {
            "id": r.movie.id,
            "title": r.movie.title,
            "poster_path": r.movie.poster_path,
            "score": r.score,
        }
        for r in ratings_qs
    ]

    paginator = Paginator(ratings, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'ratings': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'ratings.html', context)


def movie_details_view(request, movie_id):
    movie = get_object_or_404(Movie.objects.prefetch_related(
        "genres", "companies", "countries", "comments__user", "ratings"
    ), id=movie_id)

    comments = movie.comments.all().order_by('-created_at')
    form = CommentForm()
    form_error = None
    user_rating = Rating.objects.filter(user=request.user, movie=movie).first()

    if request.method == 'POST':
        if "score" in request.POST:
            score = request.POST.get("score")
            try:
                rate_movie(request.user, movie.id, int(score))
                return redirect('reelchoice_app:movie_detail', movie_id=movie.id)
            except ValidationError as e:
                form_error = str(e)

        form = CommentForm(request.POST)
        if form.is_valid():
            try:
                write_comment(request.user, movie.id, form.cleaned_data["content"])
                return redirect('reelchoice_app:movie_detail', movie_id=movie.id)
            except ValidationError as e:
                form_error = str(e)

    return render(request, "movie_detail.html", {
        "movie": movie,
        "form": form,
        "form_error": form_error,
        "comments": comments,
        "user_rating": user_rating,
        "rating_range": range(1, 11),
    })


def category_view(request, title):
    if title == "Viewers' Choice":
        movie_list = Movie.objects.order_by('-vote_average')[:50]

    elif title == "Recommended for you":
        user_ratings_qs = Rating.objects.filter(user=request.user)
        user_ratings = {r.movie_id: r.score for r in user_ratings_qs}

        recommendations = item_based_model.recommend_items(user_ratings, n_recommendations=20)
        recommended_ids = [movie_id for movie_id, _ in recommendations]

        if not recommended_ids:
            all_ids = list(Movie.objects.values_list('id', flat=True))
            recommended_ids = random.sample(all_ids, min(20, len(all_ids)))

        movie_list = Movie.objects.filter(id__in=recommended_ids)

    elif title == "Based on a true story":
        movie_list = Movie.objects.filter(overview__icontains="true story")

    elif title == "Top Horror Movies":
        movie_list = Movie.objects.filter(genres__name__iexact="Horror")

    elif title == "Rate More Movies":
        rated_ids = request.user.ratings.values_list('movie_id', flat=True)
        movie_list = Movie.objects.exclude(id__in=rated_ids)

    else:
        movie_list = Movie.objects.none()

    paginator = Paginator(movie_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "category_detail.html", {
        "title": title,
        "movies": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "page_obj": page_obj,
    })