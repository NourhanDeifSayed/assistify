import os
import logging
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
from django.conf import settings
from django.apps import apps

# Configure logging
logger = logging.getLogger(__name__)

class ProductRecommendationModel:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), 'semantic_embeddings.pkl')
        self.model = None
        self.product_embeddings = None
        self.product_ids = []
        self.is_trained = False
        self._load_model()

    def _load_model(self):
        """Load the SentenceTransformer model and pre-computed embeddings."""
        try:
            from sentence_transformers import SentenceTransformer
            # Use a multilingual model that supports Arabic and English
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("Sentence Transformer model loaded successfully.")
            
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.product_embeddings = data.get('embeddings')
                    self.product_ids = data.get('product_ids')
                    self.is_trained = True
                logger.info(f"Loaded pre-computed embeddings for {len(self.product_ids)} products.")
            else:
                logger.warning("No pre-computed product embeddings found. Please run 'python manage.py train_lightfm' to generate them.")
        except Exception as e:
            logger.error(f"Failed to load semantic recommendation model: {e}")
            self.is_trained = False

    def generate_product_embeddings(self):
        """Generate and save embeddings for all products in the database."""
        try:
            # Use Django's app registry to get the model safely
            Product = apps.get_model('products', 'Product')
            products = Product.objects.filter(is_active=True)
            
            if not products.exists():
                logger.warning("No active products found in database to generate embeddings.")
                return False

            product_texts = []
            self.product_ids = []
            
            for p in products:
                # Use only existing fields: name and description
                text = f"{p.name} {p.description}"
                product_texts.append(text)
                self.product_ids.append(p.id)

            logger.info(f"Generating embeddings for {len(product_texts)} products...")
            self.product_embeddings = self.model.encode(product_texts)
            
            # Save to disk
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'embeddings': self.product_embeddings,
                    'product_ids': self.product_ids
                }, f)
            
            self.is_trained = True
            logger.info("Product embeddings generated and saved successfully!")
            return True
        except Exception as e:
            logger.error(f"An error occurred during embedding generation: {e}")
            return False

    def predict(self, user_id: Optional[int] = None, query: str = "", intent: str = 'inquiry', sentiment: str = 'neutral') -> Dict[str, Any]:
        """Get recommendations based on semantic similarity to the query."""
        recommendations = []
        method = 'fallback_database_search'

        try:
            # 1. Try Semantic Search if model is trained
            if self.is_trained and self.model is not None and query:
                from sklearn.metrics.pairwise import cosine_similarity
                
                query_embedding = self.model.encode([query])
                similarities = cosine_similarity(query_embedding, self.product_embeddings)[0]
                
                # Get top 5 indices
                top_indices = np.argsort(similarities)[::-1][:5]
                
                Product = apps.get_model('products', 'Product')
                for idx in top_indices:
                    p_id = self.product_ids[idx]
                    try:
                        p = Product.objects.get(id=p_id)
                        recommendations.append({
                            'product_id': p.id,
                            'name': p.name,
                            'price': float(p.price),
                            'currency': 'EGP',
                            'description': p.description,
                            'score': float(similarities[idx]),
                            'emoji': '🩺'
                        })
                    except Product.DoesNotExist:
                        continue
                
                if recommendations:
                    return {
                        'recommendations': recommendations,
                        'method': 'semantic_multilingual_recommendation'
                    }

            # 2. Fallback: Smart Database Search
            Product = apps.get_model('products', 'Product')
            from django.db.models import Q
            
            q_objects = Q(is_active=True)
            if query:
                q_objects &= (Q(name__icontains=query) | Q(description__icontains=query))
            elif intent in ['purchase', 'product_search']:
                # If no query but intent is purchase, show some active products
                pass
            
            products = Product.objects.filter(q_objects)[:5]
            for p in products:
                recommendations.append({
                    'product_id': p.id,
                    'name': p.name,
                    'price': float(p.price),
                    'currency': 'EGP',
                    'description': p.description,
                    'score': 0.5,
                    'emoji': '📦'
                })
            
            return {
                'recommendations': recommendations,
                'method': 'database_fallback'
            }

        except Exception as e:
            logger.error(f"Error in product recommendation: {e}")
            return {
                'recommendations': [],
                'method': 'error_fallback'
            }
