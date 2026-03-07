import pandas as pd
import numpy as np
import warnings
from transformers import AutoTokenizer, AutoModel
import torch
import fasttext

warnings.filterwarnings('ignore')

class AraBERTEmbedder:
    def __init__(self, model_name="aubmindlab/bert-base-arabertv2"):
        print(f"loding arabert model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        print(f"model loded on {self.device}")

    def get_embedding(self, text, pooling='mean'):
        if not text or pd.isna(text):
            return np.zeros(768)
        inputs = self.tokenizer(
            str(text),
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            last_hidden_state = outputs.last_hidden_state
        if pooling == 'mean':
            embedding = last_hidden_state.mean(dim=1)[0].cpu().numpy()
        else:  
            embedding = last_hidden_state[0, 0].cpu().numpy()
        return embedding

    def get_embeddings_batch(self, texts, batch_size=32, pooling='mean'):
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_embeddings = []
            for text in batch:
                emb = self.get_embedding(text, pooling)
                batch_embeddings.append(emb)
            embeddings.extend(batch_embeddings)
            if (i + batch_size) % (batch_size * 5) == 0:
                print(f" prosed {i + batch_size}/{len(texts)} texts")
        return np.array(embeddings)

class FastTextEmbedder:
    def __init__(self, language='ar'):
        model_path = f"cc.{language}.300.bin"
        print(f"loding fasttext model for language: {language}")
        self.model = fasttext.load_model(model_path)
        print(f"model loded from {model_path}")

    def get_embedding(self, text):
        if not text or pd.isna(text):
            return np.zeros(300)
        embedding = self.model.get_sentence_vector(str(text))
        return embedding

    def get_embeddings_batch(self, texts):
        embeddings = []
        for i, text in enumerate(texts):
            emb = self.get_embedding(text)
            embeddings.append(emb)
            if (i + 1) % 100 == 0:
                print(f" prosed {i + 1}/{len(texts)} texts")
        return np.array(embeddings)

class SimpleArabicEmbedder:
    def __init__(self, embedding_dim=100):
        self.embedding_dim = embedding_dim
        self.word_vectors = {}

    def build_vocabulary(self, texts):
        from collections import Counter
        words = []
        for text in texts:
            words.extend(str(text).split())
        word_counts = Counter(words)
        self.vocabulary = {word: idx for idx, (word, _) in enumerate(word_counts.most_common())}
        np.random.seed(42)
        for word in self.vocabulary:
            self.word_vectors[word] = np.random.randn(self.embedding_dim)
        print(f"bilt vocabulary with {len(self.vocabulary)} words")

    def get_embedding(self, text):
        if not text or pd.isna(text):
            return np.zeros(self.embedding_dim)
        words = str(text).split()
        vectors = [self.word_vectors.get(word, np.random.randn(self.embedding_dim)) for word in words]
        if vectors:
            return np.mean(vectors, axis=0)
        else:
            return np.zeros(self.embedding_dim)

    def get_embeddings_batch(self, texts):
        embeddings = []
        for i, text in enumerate(texts):
            emb = self.get_embedding(text)
            embeddings.append(emb)
            if (i + 1) % 100 == 0:
                print(f" prosed {i + 1}/{len(texts)} texts")
        return np.array(embeddings)

def create_product_features(products_df, embeddings, embedding_type='arabert'):
    print("\n" + "=" * 80)
    print("creting product fetures for lightfm")
    print("=" * 80)
    n_products = len(products_df)
    embedding_dim = embeddings.shape[1]
    categories = products_df['category'].unique()
    n_categories = len(categories)
    print(f"\nembedings shape: {embeddings.shape}")
    print(f"number of categoreis: {n_categories}")
    feature_dim = embedding_dim + n_categories
    features = np.zeros((n_products, feature_dim))
    features[:, :embedding_dim] = embeddings
    for idx, row in products_df.iterrows():
        category_idx = list(categories).index(row['category'])
        features[idx, embedding_dim + category_idx] = 1.0
    print(f"\nfinal feture matrix shape: {features.shape}")
    return features, categories

def main():
    print("\n" + "=" * 80)
    print("embedings extraction for lightfm")
    print("=" * 80 + "\n")
    print("loding prosed data...")
    products_df = pd.read_csv('products_processed.csv')
    interactions_df = pd.read_csv('interactions_processed.csv')
    print(f"loded {len(products_df)} products")
    
    embedding_method = 'simple'  
    
    if embedding_method == 'arabert':
        print("\nusing arabert - best quality")
        embedder = AraBERTEmbedder()
        embeddings = embedder.get_embeddings_batch(products_df['product_name_clean'].tolist())
    elif embedding_method == 'fasttext':
        print("\nusing fasttext - fast and lightweit")
        embedder = FastTextEmbedder(language='ar')
        embeddings = embedder.get_embeddings_batch(products_df['product_name_clean'].tolist())
    else:
        print("\nusing simple embeder - no dependencies")
        embedder = SimpleArabicEmbedder(embedding_dim=100)
        all_texts = list(products_df['product_name_clean']) 
        embedder.build_vocabulary(all_texts)
        print("\nextracting embedings from product names...")
        embeddings = embedder.get_embeddings_batch(products_df['product_name_clean'].tolist())

    print(f"\nextracted embedings shape: {embeddings.shape}")
    features, categories = create_product_features(products_df, embeddings, embedding_type=embedding_method)
    
    print("\nsaving embedings and fetures")
    np.save('product_embeddings.npy', embeddings)
    np.save('product_features.npy', features)
    print("saved product_embeddings.npy")
    print("saved product_features.npy")
    print("\nembedings extraction completed succefully")
    return embeddings, features, categories

if __name__ == "__main__":
    embeddings, features, categories = main()