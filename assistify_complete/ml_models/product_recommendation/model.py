import numpy as np
from lightfm import LightFM
from lightfm.data import Dataset
import pickle

class ProductRecommender:
    def __init__(self, num_components=50, loss='bpr'):
        self.num_components = num_components
        self.loss = loss
        self.model = LightFM(no_components=num_components, loss=loss, random_state=42)
        self.dataset = None
        self.interactions = None
        self.item_features = None
        self.user_features = None
    
    def prepare_data(self, interactions_df, products_df):
        self.dataset = Dataset()
        
        self.dataset.fit(
            interactions_df['customer_id'].unique(),
            interactions_df['product_id'].unique(),
            item_features=products_df['category'].unique()
        )
        
        (self.interactions, weights) = self.dataset.build_interactions(
            [(row['customer_id'], row['product_id']) for _, row in interactions_df.iterrows()]
        )
        
        self.item_features = self.dataset.build_item_features(
            [(row['product_id'], [row['category']]) for _, row in products_df.iterrows()]
        )
        
        return self.interactions, self.item_features
    
    def train(self, epochs=30):
        if self.interactions is None:
            raise ValueError("Data not prepared. Call prepare_data first.")
        
        self.model.fit(
            self.interactions,
            item_features=self.item_features,
            epochs=epochs,
            num_threads=4,
            verbose=True
        )
    
    def recommend(self, customer_id, num_recommendations=5):
        if self.model is None:
            raise ValueError("Model not trained. Call train first.")
        
        scores = self.model.predict(customer_id, np.arange(self.interactions.shape[1]))
        top_items = np.argsort(-scores)[:num_recommendations]
        top_scores = scores[top_items]
        
        return {
            'recommendations': [
                {
                    'product_id': int(item),
                    'score': float(score),
                    'rank': i + 1
                }
                for i, (item, score) in enumerate(zip(top_items, top_scores))
            ]
        }
    
    def save(self, path):
        self.model.save(path + '/model.pkl')
        with open(path + '/dataset.pkl', 'wb') as f:
            pickle.dump(self.dataset, f)
    
    def load(self, path):
        self.model.load(path + '/model.pkl')
        with open(path + '/dataset.pkl', 'rb') as f:
            self.dataset = pickle.load(f)
