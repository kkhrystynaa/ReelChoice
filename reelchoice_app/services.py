from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Genre, Company, Country, Movie, Comment, Rating

User = get_user_model()

def rate_movie(user, movie_id, score):
    """
    Задає або оновлює рейтинг для фільму від імені user.
    - score: int від 0 до 10
    Повертає об’єкт Rating.
    """
    if not 0 <= score <= 10:
        raise ValidationError("Score must be between 0 and 10")

    movie = get_object_or_404(Movie, pk=movie_id)

    rating, created = Rating.objects.update_or_create(
        user=user,
        movie=movie,
        defaults={'score': score}
    )
    return rating


def write_comment(user, movie_id, content):
    """
    Створює коментар 'content' до фільму з movie_id від імені user.
    Повертає об’єкт Comment.
    """
    text = content.strip()
    if not text:
        raise ValidationError("Коментар не може бути порожнім")

    movie = get_object_or_404(Movie, pk=movie_id)

    comment = Comment.objects.create(
        user=user,
        movie=movie,
        content=text
    )
    return comment


def get_user_ratings_data(user):
    """
    Повертає список словників із полями:
    'title', 'poster_path', 'score'
    """
    qs = (
        Rating.objects
        .filter(user=user)
        .select_related('movie')
        .order_by('-created_at')
    )
    return [
        {
            'title': r.movie.title,
            'poster_path': r.movie.poster_path,
            'score': r.score
        }
        for r in qs
    ]


def search_movies_by_title(search_text):
    """
    Повертає фільми, назви яких починаються з `search_text` (case-insensitive),
    відсортовані за vote_average (спадання), і повертає лише поля:
    title, poster_path, vote_average.
    """
    if not search_text:
        return Movie.objects.none()

    return (
        Movie.objects
             .filter(title__istartswith=search_text)
             .order_by('-vote_average')
             .values('title', 'poster_path', 'vote_average')
    )


def get_movies_by_genre(genre_id):
    """
    Повертає QuerySet фільмів, що належать до жанру з id=genre_id,
    з полями: title, poster_path, vote_average.
    """
    return (
        Movie.objects
             .filter(genres__id=genre_id)
             .values('title', 'poster_path', 'vote_average')
    )


def get_movie_detail_info(user, movie_id):
    """
    Повертає словник з інформацією про фільм:
      - title
      - poster_path
      - runtime
      - vote_average
      - overview
      - user_rating (ціле число від 1..10 або None)
      - genres (рядок, назви через кому)
    """
    movie = get_object_or_404(
        Movie.objects.prefetch_related('genres'),
        pk=movie_id
    )

    genre_names = [g.name for g in movie.genres.all()]
    genres_str = ", ".join(genre_names)

    user_rating = None
    if user and user.is_authenticated:
        rating_qs = movie.ratings.filter(user=user).values_list('score', flat=True)
        user_rating = rating_qs[0] if rating_qs else None

    return {
        'title': movie.title,
        'poster_path': movie.poster_path,
        'runtime': movie.runtime,
        'vote_average': movie.vote_average,
        'overview': movie.overview,
        'user_rating': user_rating,
        'genres': genres_str,
    }


def get_movie_comments(movie_id):
    """
    Повертає QuerySet об’єктів Comment для фільму з id=movie_id,
    разом із username автора та created_at, відсортовані за часом.
    """
    get_object_or_404(Movie, pk=movie_id)

    comments = (
        Comment.objects
               .filter(movie_id=movie_id)
               .select_related('user')
               .order_by('created_at')
    )
    return comments
