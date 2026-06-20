import pandas as pd
import numpy as np
import warnings
from lightfm import LightFM
from lightfm.data import Dataset
from lightfm.evaluation import precision_at_k, recall_at_k, auc_score
import pickle
from scipy.sparse import csr_matrix
import joblib

warnings.filterwarnings('ignore')

class LightFMDataPreparation:
    def __init__(self):
        self.dataset = None
        self.interactions = None
        self.item_features = None
        self.user_features = None
    
    def load_data(self):
        self.products_df = pd.read_csv('products_processed.csv')
        self.interactions_df = pd.read_csv('interactions_processed.csv')
        self.product_embeddings = np.load('product_embeddings.npy')
        self.product_features = np.load('product_features.npy')
        return self
    
    def create_dataset(self):
        self.dataset = Dataset()
        self.dataset.fit(
            users=self.interactions_df['user_id'].unique(),
            items=self.interactions_df['product_id'].unique()
        )
        return self
    
    def build_interactions(self):
        interactions_data = [
            (row['user_id'], row['product_id'], row['final_weight'])
            for _, row in self.interactions_df.iterrows()
        ]
        self.interactions, self.weights = self.dataset.build_interactions(
            [(user, item) for user, item, _ in interactions_data]
        )
        self.interactions.data = np.array([w for _, _, w in interactions_data])
        return self
    
    def build_item_features(self):
        product_id_to_idx = {pid: idx for idx, pid in enumerate(self.dataset.item_identity_features)}
        n_items = len(self.dataset.item_identity_features)
        n_features = self.product_features.shape[1]
        self.item_features_matrix = csr_matrix((n_items, n_features))
        for idx, product_id in enumerate(self.dataset.item_identity_features):
            if product_id in product_id_to_idx:
                feature_idx = product_id_to_idx[product_id]
                self.item_features_matrix[idx] = self.product_features[feature_idx]
        return self
    
    def split_data(self, test_size=0.2, random_state=42):
        np.random.seed(random_state)
        n_interactions = self.interactions.nnz
        indices = np.random.permutation(n_interactions)
        test_count = int(n_interactions * test_size)
        test_indices = set(indices[:test_count])
        train_interactions = self.interactions.copy()
        test_interactions = self.interactions.copy()
        for idx in test_indices:
            row, col = np.unravel_index(idx, self.interactions.shape)
            train_interactions[row, col] = 0
        train_interactions.eliminate_zeros()
        self.train_interactions = train_interactions
        self.test_interactions = test_interactions
        return self

class LightFMTrainer:
    def __init__(self, loss='warp', k=10, learning_rate=0.05, random_state=42):
        self.model = LightFM(
            loss=loss,
            k=k,
            learning_rate=learning_rate,
            random_state=random_state,
            no_components=k
        )
        self.history = {'epoch': [], 'train_auc': [], 'test_auc': []}
    
    def train(self, train_interactions, test_interactions, item_features, epochs=50, batch_size=128, num_threads=4, verbose=True):
        print("staring traning lightfm")
        for epoch in range(epochs):
            self.model.fit(
                train_interactions,
                item_features=item_features,
                epochs=1,
                batch_size=batch_size,
                num_threads=num_threads,
                verbose=False
            )
            if (epoch + 1) % 10 == 0 and verbose:
                test_auc = auc_score(self.model, test_interactions, item_features=item_features, num_threads=num_threads).mean()
                print(f"epoch {epoch + 1} auc result is {test_auc}")
        print("traning finish")
        return self
    
    def save_model(self, model_path='lightfm_model.pkl'):
        joblib.dump(self.model, model_path)
    
    def save_history(self, history_path='training_history.pkl'):
        with open(history_path, 'wb') as f:
            pickle.dump(self.history, f)

def main():
    print("lightfm traning start")
    prep = LightFMDataPreparation()
    prep.load_data()
    prep.create_dataset()
    prep.build_interactions()
    prep.build_item_features()
    prep.split_data()
    
    trainer = LightFMTrainer(loss='warp', k=50)
    trainer.train(
        train_interactions=prep.train_interactions,
        test_interactions=prep.test_interactions,
        item_features=prep.item_features_matrix
    )
    
    trainer.save_model('lightfm_model.pkl')
    trainer.save_history('training_history.pkl')
    
    metadata = {'dataset': prep.dataset, 'products_df': prep.products_df}
    joblib.dump(metadata, 'model_metadata.pkl')
    print("metadata saved succefully")
    return trainer, prep

if __name__ == "__main__":
    trainer, prep = main()