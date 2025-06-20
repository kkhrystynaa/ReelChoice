import os
from pprint import pprint

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

    def test_recommend_items(self):
        recommendations = self.model.recommend_items(self.sample_user_ratings, n_recommendations=20)

        self.assertIsNotNone(recommendations)

        for movie_id, rating in recommendations:
            self.assertNotIn(movie_id, self.sample_user_ratings)

        ratings = [rating for _, rating in recommendations]
        self.assertEqual(ratings, sorted(ratings, reverse=True))
