from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from .models import Movie, Comment, Rating

User = get_user_model()

def rate_movie(user, movie_id, score):
    """
    Sets or updates the rating for a movie on behalf of the user.
    - score: int from 1 to 10
    Returns the Rating object.
    """
    if not 1 <= score <= 10:
        raise ValidationError("Score must be between 1 and 10")

    movie = get_object_or_404(Movie, pk=movie_id)

    rating, created = Rating.objects.update_or_create(
        user=user,
        movie=movie,
        defaults={'score': score}
    )
    return rating


def delete_rating(user, movie_id):
    """
    Deletes the rating for the movie with movie_id by the given user.
    Returns True if a rating was deleted, False if no rating existed.
    """
    rating = Rating.objects.filter(user=user, movie_id=movie_id).first()
    if rating:
        rating.delete()
        return True
    return False


def write_comment(user, movie_id, content):
    """
    Creates a comment with 'content' for the movie with movie_id on behalf of the user.
    Returns the Comment object.
    """
    text = content.strip()
    if not text:
        raise ValidationError("Comment must not be empty")

    movie = get_object_or_404(Movie, pk=movie_id)

    comment = Comment.objects.create(
        user=user,
        movie=movie,
        content=text
    )
    return comment


def delete_comment(comment_id):
    """
    Deletes a comment with the given comment_id if it belongs to the user.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()


def get_user_ratings_data(user):
    """
    Returns a list of dictionaries for the given user's movie ratings.
    Each dictionary contains the following fields:
    - 'title': the movie's title
    - 'poster_path': the path to the movie's poster
    - 'score': the user's rating score
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
    Returns a QuerySet of movies whose titles start with `search_text` (case-insensitive).
    The results are sorted by vote_average in descending order.

    Each result includes the following fields:
    - 'title': the movie's title
    - 'poster_path': the path to the movie's poster
    - 'vote_average': the movie's average rating
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
    Returns a QuerySet of movies that belong to the genre with the given genre_id.

    Each result includes the following fields:
    - 'title': the movie's title
    - 'poster_path': the path to the movie's poster
    - 'vote_average': the movie's average rating
    """
    return (
        Movie.objects
             .filter(genres__id=genre_id)
             .values('title', 'poster_path', 'vote_average')
    )


def get_movie_detail_info(user, movie_id):
    """
    Returns a dictionary with detailed information about a movie.

    Includes the following fields:
    - 'title': the movie's title
    - 'poster_path': the path to the movie's poster
    - 'runtime': the movie's duration in minutes
    - 'vote_average': the movie's average rating
    - 'overview': a short summary of the movie
    - 'user_rating': the current user's rating (integer from 1 to 10 or None)
    - 'genres': a comma-separated string of genre names
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
    Returns a QuerySet of Comment objects for the movie with the given movie_id.

    Each comment includes:
    - the user's username (via select_related)
    - the comment content and creation timestamp

    The comments are sorted by creation time (ascending).
    """
    get_object_or_404(Movie, pk=movie_id)

    comments = (
        Comment.objects
               .filter(movie_id=movie_id)
               .select_related('user')
               .order_by('created_at')
    )
    return comments
