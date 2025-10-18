import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_URL = "http://127.0.0.1:8000/api"

def process_product(product_data):
    resp = requests.post(f"{BASE_URL}/orchestrator/process", json=product_data)
    return resp.json()

def classify_product(product_data):
    resp = requests.post(f"{BASE_URL}/classifier/process", json=product_data)
    return resp.json()

def extract_attributes(product_data):
    resp = requests.post(f"{BASE_URL}/extractor/process", json=product_data)
    return resp.json()

def generate_tags(product_data):
    resp = requests.post(f"{BASE_URL}/tagger/process", json=product_data)
    return resp.json()
# src/utils/api.py
def process_product_description(description: str):
    """
    Runs attribute extraction, category classification, and tag generation 
    for a given product description.
    """
    try:
        payload = {"description": description}  # Wrap string in dict

        category = classify_product(payload)
        attributes = extract_attributes(payload)
        tags = generate_tags(payload)

        return {
            "category": category,
            "attributes": attributes,
            "tags": tags
        }
    except Exception as e:
        print(f"Error in process_product_description: {e}")
        return None
    
def get_recommended_products(query_text: str, df: pd.DataFrame, top_n: int = 5):
    """
    Get recommended products using the API search endpoint for better accuracy.
    Returns categorized results: exact_matches and other_recommendations.
    Falls back to local search if API is unavailable.
    """
    try:
        # Use the API search endpoint for better accuracy
        response = requests.get(f"{BASE_URL}/search/suggest", params={
            "q": query_text,
            "top_n": top_n
        })

        if response.status_code == 200:
            api_results = response.json()
            exact_matches = api_results.get("exact_matches", [])
            other_recommendations = api_results.get("other_recommendations", [])

            # Convert API results to DataFrame format
            result_data = []
            
            # Add exact matches first
            for result in exact_matches:
                result_data.append({
                    "productDisplayName": result.get("productDisplayName", ""),
                    "articleType": result.get("articleType", ""),
                    "baseColour": result.get("baseColour", ""),
                    "usage": result.get("usage", ""),
                    "gender": result.get("gender", ""),
                    "score": result.get("score", 0.0),
                    "filename": result.get("filename", ""),
                    "link": result.get("link", ""),
                    "match_type": "exact"
                })

            # Add other recommendations
            for result in other_recommendations:
                result_data.append({
                    "productDisplayName": result.get("productDisplayName", ""),
                    "articleType": result.get("articleType", ""),
                    "baseColour": result.get("baseColour", ""),
                    "usage": result.get("usage", ""),
                    "gender": result.get("gender", ""),
                    "score": result.get("score", 0.0),
                    "filename": result.get("filename", ""),
                    "link": result.get("link", ""),
                    "match_type": "related"
                })

            return pd.DataFrame(result_data)
    except Exception as e:
        print(f"API search failed, falling back to local search: {e}")

    # Fallback to local search if API fails
    if df.empty:
        return df

    # Combine relevant text columns for similarity
    text_columns = ["productDisplayName", "articleType", "usage", "baseColour", "gender"]
    available_cols = [col for col in text_columns if col in df.columns]
    if not available_cols:
        # fallback: first object-type column
        available_cols = [df.select_dtypes(include=["object"]).columns[0]]

    product_texts = df[available_cols[0]].fillna("")
    for col in available_cols[1:]:
        product_texts += " " + df[col].fillna("")

    # TF-IDF vectorization
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(product_texts)

    # Vectorize the query (summary)
    query_vec = tfidf.transform([query_text])

    # Cosine similarity
    sim_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # Get top N products
    top_indices = sim_scores.argsort()[::-1][:top_n]
    result_df = df.iloc[top_indices].copy()
    result_df['match_type'] = 'related'  # Default to related for fallback
    return result_df
