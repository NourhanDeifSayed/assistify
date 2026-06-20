import pandas as pd
import numpy as np
import re
import warnings
import kagglehub
import os

warnings.filterwarnings('ignore')

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = " ".join(text.split())
    return text

def load_real_flipkart_data():
    print("donloding flipkart dataset from kaggle...")
    path = kagglehub.dataset_download("atharvjairath/flipkart-ecommerce-dataset")
    csv_path = os.path.join(path, "flipkart_com-ecommerce_sample.csv")
    
    print(f"loding data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    df['product_name_clean'] = df['product_name'].apply(clean_text)
    
    def extract_category(tree):
        try:
            cat = tree.strip('[]"').split(' >> ')[0]
            return cat
        except:
            return "unknown"
            
    df['category'] = df['product_category_tree'].apply(extract_category)
    
    products_df = df[['uniq_id', 'product_name', 'product_name_clean', 'category', 'retail_price', 'discounted_price', 'image', 'description']].copy()
    products_df.rename(columns={'uniq_id': 'product_id'}, inplace=True)
    products_df = products_df.dropna(subset=['retail_price'])
    
    print("genrating synthtic interctions for the dataset...")
    n_users = 1000
    n_interactions = 10000
    product_ids = products_df['product_id'].values
    user_ids = [f"user_{i}" for i in range(1, n_users + 1)]
    
    interactions_data = {
        'user_id': np.random.choice(user_ids, n_interactions),
        'product_id': np.random.choice(product_ids, n_interactions),
        'rating': np.random.randint(1, 6, n_interactions),
        'interaction_type': np.random.choice(['purchase', 'view', 'add_to_cart', 'wishlist'], n_interactions, p=[0.3, 0.4, 0.2, 0.1]),
        'timestamp': pd.date_range('2023-01-01', periods=n_interactions, freq='H')
    }
    
    interactions_df = pd.DataFrame(interactions_data)
    interactions_df = interactions_df.sort_values('rating', ascending=False).drop_duplicates(
        subset=['user_id', 'product_id'], keep='first'
    )
    
    return products_df, interactions_df

def prepare_data(products_df, interactions_df):
    print("=" * 80)
    print("data prepartion for lightfm")
    print("=" * 80)
    
    print("\n1/4 preparting interctions...")
    interaction_weights = {
        'purchase': 1.0,
        'add_to_cart': 0.7,
        'view': 0.3,
        'wishlist': 0.5
    }
    
    interactions_df['weight'] = interactions_df['interaction_type'].map(interaction_weights)
    interactions_df['final_weight'] = (interactions_df['rating'] / 5.0) * interactions_df['weight']
    
    user_ids = interactions_df['user_id'].unique()
    product_ids = products_df['product_id'].unique()
    
    user_id_map = {uid: idx for idx, uid in enumerate(user_ids)}
    product_id_map = {pid: idx for idx, pid in enumerate(product_ids)}
    
    interactions_df = interactions_df[interactions_df['product_id'].isin(product_id_map)].copy()
    interactions_df['user_idx'] = interactions_df['user_id'].map(user_id_map)
    interactions_df['product_idx'] = interactions_df['product_id'].map(product_id_map)
    
    categories = products_df['category'].unique()
    category_map = {cat: idx for idx, cat in enumerate(categories)}
    products_df['category_idx'] = products_df['category'].map(category_map)
    
    print(f"total prodcts: {len(products_df)}")
    print(f"total users: {len(user_ids)}")
    print(f"total interctions: {len(interactions_df)}")
    
    return {
        'products_df': products_df,
        'interactions_df': interactions_df,
        'user_id_map': user_id_map,
        'product_id_map': product_id_map,
        'category_map': category_map
    }

if __name__ == "__main__":
    products_df, interactions_df = load_real_flipkart_data()
    data_dict = prepare_data(products_df, interactions_df)
    
    output_dir = os.getcwd() 
    
    data_dict['products_df'].to_csv(os.path.join(output_dir, 'products_processed.csv'), index=False)
    data_dict['interactions_df'].to_csv(os.path.join(output_dir, 'interactions_processed.csv'), index=False)
    
    print("\ndata prepartion finish succefuly")