import pandas as pd
import numpy as np
import joblib
import pickle
import warnings
from scipy.sparse import csr_matrix

warnings.filterwarnings('ignore')

class RecommendationEngine:
    def __init__(self, model_path='lightfm_model.pkl', metadata_path='model_metadata.pkl'):
        print("loding traned model now")
        self.model = joblib.load(model_path)
        self.metadata = joblib.load(metadata_path)
        self.dataset = self.metadata['dataset']
        self.products_df = self.metadata['products_df']
        self.interactions_df = self.metadata['interactions_df']
        self.product_embeddings = self.metadata['product_embeddings']
        self.product_features = self.metadata['product_features']
        print("model loded succesfully")
    
    def get_user_recommendations(self, user_id, n_recommendations=5):
        try:
            user_idx = self.dataset.mapping()[0][user_id]
        except:
            return {'error': 'user not found', 'recommendations': []}
        
        predictions = self.model.predict(user_idx, np.arange(len(self.dataset.item_identity_features)))
        top_indices = np.argsort(-predictions)[:n_recommendations]
        
        recommendations = []
        for rank, item_idx in enumerate(top_indices, 1):
            product_id = self.dataset.item_identity_features[item_idx]
            product = self.products_df[self.products_df['product_id'] == product_id].iloc[0]
            recommendations.append({
                'rank': rank,
                'product_id': int(product_id),
                'product_name': product['product_name_ar'],
                'score': float(predictions[item_idx])
            })
        return recommendations

    def get_similar_products(self, product_id, n_similar=5):
        try:
            product_idx = list(self.dataset.item_identity_features).index(product_id)
        except:
            return {'error': 'product not found'}
            
        product_embedding = self.product_embeddings[product_idx]
        similarities = []
        for idx, emb in enumerate(self.product_embeddings):
            if idx != product_idx:
                similarity = np.dot(product_embedding, emb) / (np.linalg.norm(product_embedding) * np.linalg.norm(emb) + 1e-8)
                similarities.append((idx, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in similarities[:n_similar]]
        
        similar_products = []
        for rank, item_idx in enumerate(top_indices, 1):
            product = self.products_df[self.products_df['product_id'] == self.dataset.item_identity_features[item_idx]].iloc[0]
            similar_products.append({
                'rank': rank,
                'name': product['product_name_ar'],
                'similarity': float(similarities[rank-1][1])
            })
        return similar_products

    def search_products(self, query, n_results=5):
        print(f"serching for {query}")
        m1 = self.products_df[self.products_df['product_name_ar'].str.contains(query, case=False, na=False)]
        m2 = self.products_df[self.products_df['product_name_en'].str.contains(query, case=False, na=False)]
        matches = pd.concat([m1, m2]).drop_duplicates(subset=['product_id']).head(n_results)
        
        results = []
        for rank, (_, product) in enumerate(matches.iterrows(), 1):
            results.append({'rank': rank, 'name': product['product_name_ar'], 'price': float(product['price'])})
        return results

def demonstrate():
    print("staring inference demo")
    engine = RecommendationEngine()
    
    print("testing user recomndation")
    recs = engine.get_user_recommendations(user_id=1)
    print(f"found {len(recs)} results")
    
    print("testing serch function")
    search = engine.search_products(query='panadol')
    print(f"serch done with {len(search)} matches")
    
    print("inference procses complted")

if __name__ == "__main__":
    demonstrate()