import os
import pickle

import pandas as pd


class ItemBasedCF:
    def __init__(self, n_similar_items: int = 200):
        self.n_similar_items: int = n_similar_items
        self.item_similarities: dict = {}
        self.item_means: pd.Series = pd.Series(dtype=float)
        self.all_items: list = []

    def fit(self, ratings_df: pd.DataFrame):
        """Train the model on ratings data"""
        print("Building user-item matrix...")
        user_item_matrix = ratings_df.pivot(index='userId', columns='id', values='rating')

        self.all_items = list(user_item_matrix.columns)

        print("Calculating item mean ratings...")
        self.item_means = user_item_matrix.mean(axis=0, skipna=True)

        print("Computing item similarities...")
        item_similarity_df = user_item_matrix.corr(method='pearson', min_periods=10)
        item_similarity_df = item_similarity_df.fillna(0)

        similarity_upper_bound = 0.99

        for i, current_item_id in enumerate(self.all_items):
            sim_scores_for_current_item = item_similarity_df.loc[current_item_id]
            mask = (sim_scores_for_current_item > 0) & (sim_scores_for_current_item < similarity_upper_bound)
            filtered_scores = sim_scores_for_current_item[mask]
            top_n_similar_items = filtered_scores.nlargest(self.n_similar_items)
            self.item_similarities[current_item_id] = top_n_similar_items.to_dict()

        print(f"Training complete! Computed similarities for {len(self.item_similarities)} items")

    def predict_score(self, user_ratings: dict[int, float], target_item: int):
        """
        Predict score for a target item based on user's existing ratings.
        Ratings should be ordered from oldest to newest
        """

        # Check if target_item is known and has similarity data and mean rating
        if target_item not in self.item_means or target_item not in self.item_similarities:
            return None

        similar_items_to_target = self.item_similarities[target_item]
        target_item_mean = self.item_means[target_item]

        numerator = 0
        denominator = 0
        ratings_count = len(user_ratings)
        last_ratings_boost = 1

        for i, (item_id, user_rating) in enumerate(user_ratings.items()):
            if item_id in similar_items_to_target and item_id in self.item_means:
                similarity = similar_items_to_target[item_id]
                centered_rating = user_rating - self.item_means[item_id]
                if i == ratings_count - 1:
                    last_ratings_boost = 3
                elif i == ratings_count - 2:
                    last_ratings_boost = 2.5
                elif i == ratings_count - 3:
                    last_ratings_boost = 2

                numerator += similarity * centered_rating
                denominator += similarity  # Assuming similarity scores are positive due to filtering in fit

        if denominator == 0:
            # No similar items rated by the user that can be used for prediction
            return None

        score = target_item_mean + (numerator / denominator * last_ratings_boost)
        return score

    def recommend_items(self, user_ratings: dict[int, float], n_recommendations: int = 10):
        """Generate recommendations for a user"""
        candidate_items = set(self.all_items) - set(user_ratings.keys())

        predictions = []
        for item in candidate_items:
            score = self.predict_score(user_ratings, item)
            if score is not None:
                predictions.append((item, score))

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n_recommendations]

    def save_model(self, filepath: str):
        """Save the trained model"""
        model_data = {'item_similarities': self.item_similarities, 'item_means': self.item_means,
                      'n_similar_items': self.n_similar_items, 'all_items': self.all_items}
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

    def load_model(self, filepath: str):
        """Load a trained model"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file {filepath} not found")

        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.item_similarities = model_data['item_similarities']
        self.item_means = model_data['item_means']
        self.n_similar_items = model_data['n_similar_items']
        self.all_items = model_data['all_items']
