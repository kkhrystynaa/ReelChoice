from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from reelchoice_app.models import Movie, Genre, Rating, Comment
from reelchoice_app.services import (
    search_movies_by_title,
    get_movies_by_genre,
    rate_movie,
    write_comment,
    get_movie_detail_info,
    get_movie_comments,
    get_user_ratings_data,
    delete_rating,
    delete_comment
)

User = get_user_model()

class ServicesTestCase(TestCase):

    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username="alice", password='testpass')
        self.user2 = User.objects.create_user(username="bob", password='testpass')

        # Create genres
        self.genre_action = Genre.objects.create(name="Action")
        self.genre_scifi = Genre.objects.create(name="Science Fiction")
        self.genre_drama = Genre.objects.create(name="Drama")

        # Create movies
        self.movie1 = Movie.objects.create(
            id=1,
            title="Inception",
            poster_path="/inception.jpg",
            runtime=148,
            vote_average=8.8,
            overview="Dreams within dreams."
        )
        self.movie2 = Movie.objects.create(
            id=2,
            title="Interstellar",
            poster_path="/interstellar.jpg",
            vote_average=8.6
        )

        # Link movies with genres
        self.movie1.genres.add(self.genre_action, self.genre_scifi)
        self.movie2.genres.add(self.genre_scifi)

        # Create comments
        self.comment1 = Comment.objects.create(
            user=self.user1,
            movie=self.movie1,
            content="Amazing film!"
        )

        self.comment2 = Comment.objects.create(
            user=self.user2,
            movie=self.movie1,
            content="Mind-blowing."
        )

        # Create ratings
        Rating.objects.create(user=self.user2, movie=self.movie1, score=9)
        Rating.objects.create(user=self.user2, movie=self.movie2, score=8)


    def test_search_exact_match(self):
        result = list(search_movies_by_title("Inception"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], "Inception")

    def test_search_partial_match(self):
        titles = [m['title'] for m in search_movies_by_title("I")]
        self.assertListEqual(sorted(titles), ["Inception", "Interstellar"])

    def test_search_no_match(self):
        result = list(search_movies_by_title("Marvel"))
        self.assertEqual(result, [])


    def test_get_movies_by_genre_action(self):
        qs = get_movies_by_genre(self.genre_action.id)
        titles = sorted([m['title'] for m in qs])
        self.assertListEqual(titles, ["Inception"])

    def test_get_movies_by_genre_drama(self):
        qs = get_movies_by_genre(self.genre_scifi.id)
        titles = sorted([m['title'] for m in qs])
        self.assertListEqual(titles, ["Inception", "Interstellar"])

    def test_get_movies_by_genre_no_movies(self):
        qs = get_movies_by_genre(self.genre_drama.id)
        self.assertEqual(list(qs), [])


    def test_rate_movie_first_time(self):
        rating = rate_movie(self.user1, self.movie1.id, 9)
        self.assertEqual(Rating.objects.count(), 3)
        self.assertEqual(rating.user, self.user1)
        self.assertEqual(rating.movie, self.movie1)
        self.assertEqual(rating.score, 9)

    def test_update_existing_rating(self):
        Rating.objects.create(user=self.user1, movie=self.movie2, score=7)
        updated_rating = rate_movie(self.user1, self.movie2.id, 10)
        self.assertEqual(Rating.objects.count(), 3)
        self.assertEqual(updated_rating.score, 10)

    def test_invalid_movie_id_raises_404(self):
        from django.http import Http404
        with self.assertRaises(Http404):
            rate_movie(self.user1, movie_id=999, score=8)

    def test_rating_above_max_raises_validation_error(self):
        rating = Rating(user=self.user1, movie=self.movie1, score=11)
        with self.assertRaises(ValidationError):
            rating.full_clean()


    def test_write_comment_creates_comment(self):
        content = "Great movie!"
        comment = write_comment(self.user1, self.movie1.id, content)
        self.assertIsNotNone(comment.id)
        self.assertEqual(comment.user, self.user1)
        self.assertEqual(comment.movie, self.movie1)
        self.assertEqual(comment.content, content)
        self.assertIsNotNone(comment.created_at)

    def test_write_comment_for_invalid_movie_raises_404(self):
        from django.http import Http404
        with self.assertRaises(Http404):
            write_comment(self.user1, movie_id=999, content="Test comment")

    def test_write_comment_with_empty_content_raises_validation(self):
        with self.assertRaises(ValidationError):
            write_comment(self.user1, self.movie2.id, "")
        with self.assertRaises(ValidationError):
            write_comment(self.user1, self.movie2.id, "    ")


    def test_movie_detail_without_user_rating(self):
        data = get_movie_detail_info(self.user1, self.movie1.id)
        self.assertEqual(data["title"], "Inception")
        self.assertEqual(data["poster_path"], "/inception.jpg")
        self.assertEqual(data["runtime"], 148)
        self.assertEqual(data["vote_average"], 8.8)
        self.assertEqual(data["overview"], "Dreams within dreams.")
        self.assertIn(data["genres"], "Action, Science Fiction")
        self.assertIsNone(data["user_rating"])

    def test_movie_detail_with_user_rating(self):
        Rating.objects.create(user=self.user1, movie=self.movie1, score=9)
        data = get_movie_detail_info(self.user1, self.movie1.id)
        self.assertEqual(data["user_rating"], 9)

    def test_invalid_movie_id_in_detail_raises_404(self):
        from django.http import Http404
        with self.assertRaises(Http404):
            get_movie_detail_info(self.user1, 999)


    def test_get_comments_for_movie(self):
        comments = get_movie_comments(self.movie1.id)
        self.assertEqual(len(comments), 2)
        users = [c.user.username for c in comments]
        contents = [c.content for c in comments]
        self.assertIn("alice", users)
        self.assertIn("bob", users)
        self.assertIn("Amazing film!", contents)
        self.assertIn("Mind-blowing.", contents)

    def test_comment_ordering_by_created_at(self):
        comments = list(get_movie_comments(self.movie1.id))
        self.assertLessEqual(comments[0].created_at, comments[1].created_at)

    def test_non_existing_movie_raises_404(self):
        from django.http import Http404
        with self.assertRaises(Http404):
            get_movie_comments(999)


    def test_returns_only_user_ratings(self):
        data = list(get_user_ratings_data(self.user2))
        self.assertEqual(len(data), 2)
        titles = [item['title'] for item in data]
        scores = [item['score'] for item in data]
        self.assertIn("Inception", titles)
        self.assertIn("Interstellar", titles)
        self.assertIn(9, scores)
        self.assertIn(8, scores)

    def test_no_ratings_returns_empty_list(self):
        new_user = User.objects.create_user(username="no_ratings", password="no_ratings")
        data = list(get_user_ratings_data(new_user))
        self.assertEqual(data, [])


    def test_delete_rating_if_exists(self):
        self.assertEqual(Rating.objects.count(), 2)
        result = delete_rating(self.user2, self.movie1.id)
        self.assertTrue(result)
        self.assertEqual(Rating.objects.count(), 1)

    def test_delete_rating_if_not_exists(self):
        result = delete_rating(self.user1, self.movie1.id)
        self.assertFalse(result)


    def test_delete_comment_success(self):
        self.assertEqual(Comment.objects.count(), 2)
        delete_comment(self.comment1.id)
        self.assertEqual(Comment.objects.count(), 1)

    def test_delete_comment_invalid_id(self):
        invalid_id = self.comment2.id
        self.comment2.delete()
        with self.assertRaisesMessage(Exception, 'No Comment matches the given query.'):
            delete_comment(invalid_id)