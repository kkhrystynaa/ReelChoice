import os

from django.conf import settings
from django.test import TestCase

from recommender.recommender import ItemBasedCF


class TestRecommendations(TestCase):
    def setUp(self):
        self.model = ItemBasedCF()
        model_path = os.path.join(settings.BASE_DIR, 'recommender', 'trained_model.pkl')
        self.model.load_model(model_path)

        self.sample_user_ratings = {
            27205: 10.0,  # Inception
            157336: 9.0,  # Interstellar
            155: 6.0,  # The Dark Knight
            19995: 8.0,  # Avatar
            24428: 8.0  # The Avengers
        }

    def test_model_loaded_successfully(self):
        self.assertIsNotNone(self.model.item_similarities)
        self.assertIsNotNone(self.model.item_means)
        self.assertIsNotNone(self.model.all_items)
        self.assertGreater(len(self.model.all_items), 0)

    def test_predict_rating(self):
        test_movie_id = 550  # Fight Club

        if test_movie_id in self.model.item_similarities and test_movie_id in self.model.item_means:
            predicted_rating = self.model.predict_rating(self.sample_user_ratings, test_movie_id)
            self.assertIsNotNone(predicted_rating)
            self.assertGreaterEqual(predicted_rating, 1.0)
            self.assertLessEqual(predicted_rating, 10.0)
        else:
            self.skipTest(f"Movie ID {test_movie_id} not found in the similarities to user ratings")

    def test_recommend_items(self):
        recommendations = self.model.recommend_items(self.sample_user_ratings, n_recommendations=20)

        self.assertIsNotNone(recommendations)

        for movie_id, rating in recommendations:
            self.assertNotIn(movie_id, self.sample_user_ratings)
            self.assertGreaterEqual(rating, 1.0)
            self.assertLessEqual(rating, 10.0)

        ratings = [rating for _, rating in recommendations]
        self.assertEqual(ratings, sorted(ratings, reverse=True))
