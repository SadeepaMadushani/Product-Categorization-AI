"""
Information Retrieval module for product search and recommendations.
Provides TF-IDF based similarity search and product recommendations.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)


class InformationRetrieval:
    """
    Advanced information retrieval system using TF-IDF and cosine similarity.
    """
    
    # Class-level cache 

    _shared_instances = {}
    
    def __init__(self, product_database: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize with product database.
        
        Args:
            product_database: List of product dictionaries with at least 'description' field
        """
        self.product_database = product_database or []
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 3),  
            min_df=1,
            max_df=0.95,
            lowercase=True
        )
        self.tfidf_matrix = None
        self.product_ids = []
        self.is_indexed = False
        
        # Auto-build index if database is provided
        if self.product_database:
            self.build_index()
    
    @classmethod
    def get_shared_instance(cls, data_path: str = None):
        """
        Get or create a shared instance with cached index.
        
        Args:
            data_path: Path to the data file for caching key
            
        Returns:
            Shared InformationRetrieval instance
        """
        cache_key = data_path or "default"
        
        if cache_key not in cls._shared_instances:
            cls._shared_instances[cache_key] = cls()
        
        return cls._shared_instances[cache_key]
        
    def build_index(self) -> None:
        """
        Build search index from product database.
        """
        if not self.product_database:
            logger.warning("No product database provided for indexing")
            return
            
        try:
            # Extract descriptions for indexing

            descriptions = []
            self.product_ids = []
            
            for product in self.product_database:
                if isinstance(product, dict) and 'description' in product:
                    descriptions.append(str(product['description']))
                    self.product_ids.append(product.get('id', len(self.product_ids)))
                elif isinstance(product, str):
                    descriptions.append(product)
                    self.product_ids.append(len(self.product_ids))
            
            if not descriptions:
                logger.warning("No valid descriptions found in product database")
                return
                
            # Build TF-IDF matrix

            self.tfidf_matrix = self.vectorizer.fit_transform(descriptions)
            self.is_indexed = True
            logger.info(f"Successfully built index for {len(descriptions)} products")
            
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")
            self.is_indexed = False
    
    def search_products(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar products based on query.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries with product_id, similarity score, and product info
        """
        return self._search_products_impl(query, top_k)
    
    def search_similar_products(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Alias for search_products for backward compatibility.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries with product_id, similarity score, and product info
        """
        return self._search_products_impl(query, top_k)
    
    def _search_products_impl(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Internal implementation of product search with enhanced accuracy.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries with product_id, similarity score, and product info
        """
        if not self.is_indexed or self.tfidf_matrix is None:
            logger.warning("Index not built. Call build_index() first.")
            return []
            
        try:
            # Preprocess query for better matching
            processed_query = self._preprocess_query(query)
            
            # Transform query to TF-IDF vector
            query_vector = self.vectorizer.transform([processed_query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # Apply color and type boosting
            similarities = self._apply_boosting(query, similarities)
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Build results
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include products with similarity
                    product_id = self.product_ids[idx]
                    product_info = self._get_product_info(product_id)
                    
                    results.append({
                        'product_id': product_id,
                        'similarity': float(similarities[idx]),
                        'product_name': product_info.get('name', 'Unknown'),
                        'description': product_info.get('description', ''),
                        'category': product_info.get('category', 'Unknown')
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []
    
    def _preprocess_query(self, query: str) -> str:
        """
        Preprocess search query for better matching.
        
        Args:
            query: Original query string
            
        Returns:
            Preprocessed query string
        """
        # Convert to lowercase

        query = query.lower()
        
        # Expand common abbreviations

        expansions = {
            'jean': 'jeans',
            'pant': 'pants',
            'shirt': 'shirts',
            'dress': 'dresses',
            'shoe': 'shoes',
            'bag': 'bags'
        }
        
        for short, long in expansions.items():
            query = re.sub(r'\b' + short + r'\b', long, query)
        
        
        #Add colour variation

        color_variations = {
            'blue': 'blue navy royal sky',
            'red': 'red crimson scarlet',
            'green': 'green emerald forest',
            'black': 'black dark charcoal',
            'white': 'white cream ivory',
            'brown': 'brown tan beige',
            'gray': 'gray grey silver',
            'pink': 'pink rose magenta',
            'purple': 'purple violet lavender',
            'yellow': 'yellow gold amber'
        }
        
        for color, variations in color_variations.items():
            if color in query:
                query += ' ' + variations
        
        return query
    
    def _apply_boosting(self, query: str, similarities: np.ndarray) -> np.ndarray:
        """
        Apply boosting for color and product type matches.
        
        Args:
            query: Original query string
            similarities: Array of similarity scores
            
        Returns:
            Boosted similarity scores
        """
        boosted_similarities = similarities.copy()
        
        try:
            # Extract colors and product types from query
            colors = self._extract_colors(query)
            product_types = self._extract_product_types(query)
            
            # Apply boosting
            for i, product_id in enumerate(self.product_ids):
                product_info = self._get_product_info(product_id)
                boost_factor = 1.0
                
                # Color boosting
                if colors:
                    product_text = ' '.join([
                        str(product_info.get('name', '')),
                        str(product_info.get('description', '')),
                        str(product_info.get('baseColour', '')),
                        str(product_info.get('articleType', ''))
                    ]).lower()
                    
                    for color in colors:
                        if color in product_text:
                            boost_factor *= 1.5  # 50% boost for color match
                            break
                
                # Product type boosting

                if product_types:
                    product_text = ' '.join([
                        str(product_info.get('name', '')),
                        str(product_info.get('description', '')),
                        str(product_info.get('articleType', ''))
                    ]).lower()
                    
                    for ptype in product_types:
                        if ptype in product_text:
                            boost_factor *= 1.3  # 30% boost for type match
                            break
                
                boosted_similarities[i] *= boost_factor
                
        except Exception as e:
            logger.error(f"Error applying boosting: {str(e)}")
        
        return boosted_similarities
    
    def _extract_colors(self, query: str) -> List[str]:
        """Extract color terms from query."""
        colors = ['red', 'blue', 'green', 'black', 'white', 'brown', 'gray', 'grey', 
                 'pink', 'purple', 'yellow', 'orange', 'navy', 'royal', 'sky', 'crimson',
                 'scarlet', 'emerald', 'forest', 'dark', 'charcoal', 'cream', 'ivory',
                 'tan', 'beige', 'silver', 'rose', 'magenta', 'violet', 'lavender',
                 'gold', 'amber']
        
        found_colors = []
        query_lower = query.lower()
        for color in colors:
            if color in query_lower:
                found_colors.append(color)
        
        return found_colors
    
    def _extract_product_types(self, query: str) -> List[str]:
        """Extract product type terms from query."""
        types = ['jean', 'jeans', 'pant', 'pants', 'shirt', 'shirts', 'dress', 'dresses',             
                'shoe', 'shoes', 'bag', 'bags', 'jacket', 'jackets', 'coat', 'coats',
                'sweater', 'sweaters', 'hoodie', 'hoodies', 't-shirt', 'tshirt',
                'blouse', 'blouses', 'skirt', 'skirts', 'short', 'shorts']
        
        found_types = []
        query_lower = query.lower()
        for ptype in types:
            if ptype in query_lower:
                found_types.append(ptype)
        
        return found_types
    
    def get_recommendations(self, product_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Get product recommendations based on a product ID.
        
        Args:
            product_id: ID of the product to get recommendations for
            top_k: Number of recommendations to return
            
        Returns:
            List of recommended products
        """
        if not self.is_indexed or self.tfidf_matrix is None:
            logger.warning("Index not built. Call build_index() first.")
            return []
            
        try:
            # Find the product index

            product_idx = None
            for i, pid in enumerate(self.product_ids):
                if str(pid) == str(product_id):
                    product_idx = i
                    break
                    
            if product_idx is None:
                logger.warning(f"Product ID {product_id} not found in database")
                return []
            
            # Get similarity scores for this product

            similarities = cosine_similarity(
                self.tfidf_matrix[product_idx:product_idx+1], 
                self.tfidf_matrix
            ).flatten()
            
            # Get top-k similar products (excluding the product itself)
            top_indices = np.argsort(similarities)[::-1][1:top_k+1]
            
            # Build results
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:
                    pid = self.product_ids[idx]
                    product_info = self._get_product_info(pid)
                    
                    results.append({
                        'product_id': pid,
                        'similarity': float(similarities[idx]),
                        'product_name': product_info.get('name', 'Unknown'),
                        'description': product_info.get('description', ''),
                        'category': product_info.get('category', 'Unknown')
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Transform texts to TF-IDF vectors
            vectors = self.vectorizer.transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def update_index(self, new_products: List[Dict[str, Any]]) -> None:
        """
        Update search index with new products.
        
        Args:
            new_products: List of new product dictionaries
        """
        try:
            # Add new products to database
            self.product_database.extend(new_products)
            
            # Rebuild index
            self.build_index()
            
            logger.info(f"Successfully updated index with {len(new_products)} new products")
            
        except Exception as e:
            logger.error(f"Error updating index: {str(e)}")
    
    def _get_product_info(self, product_id: str) -> Dict[str, Any]:
        """
        Get product information by ID.
        
        Args:
            product_id: Product ID to look up
            
        Returns:
            Product information dictionary
        """
        for product in self.product_database:
            if isinstance(product, dict) and str(product.get('id', '')) == str(product_id):
                return product
            elif isinstance(product, str) and str(self.product_ids.index(product_id)) == str(product_id):
                return {'description': product, 'name': f'Product {product_id}'}
        
        return {'name': 'Unknown', 'description': '', 'category': 'Unknown'}
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current index.
        
        Returns:
            Dictionary with index statistics
        """
        return {
            'total_products': len(self.product_database),
            'indexed_products': len(self.product_ids) if self.is_indexed else 0,
            'is_indexed': self.is_indexed,
            'vocabulary_size': len(self.vectorizer.vocabulary_) if self.is_indexed else 0
        }
