import os
import joblib
import pandas as pd
import numpy as np

class RecommendationService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RecommendationService, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        try:
            self.model = joblib.load(os.path.join(base_path, 'recommendation_model.pkl'))
            self.encoders = joblib.load(os.path.join(base_path, 'encoders.pkl'))
            self.df = joblib.load(os.path.join(base_path, 'product_data.pkl'))
            self.is_loaded = True
        except Exception as e:
            print(f"Error loading recommendation model: {e}")
            self.is_loaded = False

    def get_recommendations(self, product_name, n_recommendations=5):
        if not self.is_loaded:
            return []

        matches = self.df[self.df['Model'].str.contains(product_name, case=False, na=False)]
        
        if matches.empty:
            brand_matches = self.df[self.df['Brand'].str.contains(product_name, case=False, na=False)]
            if not brand_matches.empty:
                return brand_matches.head(n_recommendations).to_dict('records')
            return self.df.head(n_recommendations).to_dict('records')

       
        idx = matches.index[0]
        product_features = []
        for col in ['Brand', 'Model', 'Color']:
            val = str(self.df.iloc[idx][col])
           
            if val in self.encoders[col].classes_:
                product_features.append(self.encoders[col].transform([val])[0])
            else:
                product_features.append(0) 

        distances, indices = self.model.kneighbors([product_features], n_neighbors=n_recommendations + 1)
        
       
        rec_indices = indices[0][1:]
        recommendations = self.df.iloc[rec_indices].to_dict('records')
        
        return recommendations


recommendation_service = RecommendationService()
