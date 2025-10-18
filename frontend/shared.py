import streamlit as st
import pandas as pd
import requests
import os

# Configuration
API_BASE_URL = "http://localhost:8000/api"

# Resolve data path dynamically
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH_CANDIDATES = [
    os.path.join(PROJECT_ROOT, "backend", "data", "cleaned_product_data.csv"),
    os.path.join(PROJECT_ROOT, "backend", "data", "product.csv"),
]

def call_api(endpoint, data=None, method="POST"):
    """Generic API call function"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def load_product_data():
    """Load product data from CSV file with the correct structure"""
    try:
        # pick the first existing path from candidates
        data_path = None
        for candidate in DATA_PATH_CANDIDATES:
            if os.path.exists(candidate):
                data_path = candidate
                break

        if data_path and os.path.exists(data_path):
            df = pd.read_csv(data_path)
            
            # Create tags from available attributes for better discovery
            df['tags'] = df.apply(lambda row: [
                row['gender'],
                row['masterCategory'],
                row['subCategory'],
                row['articleType'],
                row['baseColour'],
                row['season'],
                str(int(row['year'])) if pd.notna(row['year']) else '',
                row['usage']
            ], axis=1)
            
            # Clean up tags - remove empty values and flatten
            df['tags'] = df['tags'].apply(lambda x: [tag for tag in x if tag and str(tag).strip() != ''])
            
            st.session_state.admin_data = df
            return df
        else:
            st.warning("Product data file not found locally. Using sample data.")
            return load_sample_data()
    except Exception as e:
        st.error(f"Error loading product data: {str(e)}")
        return load_sample_data()

def load_sample_data():
    """Load sample product data for demonstration if real data is unavailable"""
    sample_data = [
        {
            "id": 15970,
            "gender": "Men",
            "masterCategory": "Apparel",
            "subCategory": "Topwear",
            "articleType": "Shirts",
            "baseColour": "Navy Blue",
            "season": "Autumn",
            "year": 2011.0,
            "usage": "Casual",
            "productDisplayName": "Turtle Check Men Navy Blue Shirt",
            "filename": "15970.jpg",
            "link": "http://assets.myntassets.com/v1/images/style/properties/7a5b82d1372a7a5c6de67ae7a314fd91_images.jpg"
        },
        {
            "id": 39386,
            "gender": "Men",
            "masterCategory": "Apparel",
            "subCategory": "Bottomwear",
            "articleType": "Jeans",
            "baseColour": "Blue",
            "season": "Summer",
            "year": 2012.0,
            "usage": "Casual",
            "productDisplayName": "Peter England Men Party Blue Jeans",
            "filename": "39386.jpg",
            "link": "http://assets.myntassets.com/v1/images/style/properties/4850873d0c417e6480a26059f83aac29_images.jpg"
        },
        {
            "id": 59263,
            "gender": "Women",
            "masterCategory": "Accessories",
            "subCategory": "Watches",
            "articleType": "Watches",
            "baseColour": "Silver",
            "season": "Winter",
            "year": 2016.0,
            "usage": "Casual",
            "productDisplayName": "Titan Women Silver Watch",
            "filename": "59263.jpg",
            "link": "http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg"
        }
    ]
    df = pd.DataFrame(sample_data)
    df['tags'] = df.apply(lambda row: [
        row['gender'],
        row['masterCategory'],
        row['subCategory'],
        row['articleType'],
        row['baseColour'],
        row['season'],
        str(int(row['year'])) if pd.notna(row['year']) else '',
        row['usage']
    ], axis=1)
    return df

def get_categories():
    """Get available categories from the actual data"""
    df = load_product_data()
    if df is not None and 'masterCategory' in df.columns:
        return sorted(df['masterCategory'].unique().tolist())
    return ["Apparel", "Accessories", "Footwear"]

def get_subcategories(category=None):
    """Get available subcategories"""
    df = load_product_data()
    if df is not None and 'subCategory' in df.columns:
        if category:
            return sorted(df[df['masterCategory'] == category]['subCategory'].unique().tolist())
        return sorted(df['subCategory'].unique().tolist())
    return ["Topwear", "Bottomwear", "Watches"]

def get_article_types(subcategory=None):
    """Get available article types"""
    df = load_product_data()
    if df is not None and 'articleType' in df.columns:
        if subcategory:
            return sorted(df[df['subCategory'] == subcategory]['articleType'].unique().tolist())
        return sorted(df['articleType'].unique().tolist())
    return ["Shirts", "Jeans", "Watches"]