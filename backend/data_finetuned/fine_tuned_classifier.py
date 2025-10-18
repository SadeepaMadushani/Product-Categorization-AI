import torch
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
import json
import os

from .fine_tuning import ProductCategorizationFineTuner

logger = logging.getLogger(__name__)

class FineTunedCategoryClassifier:
    def __init__(self, model_path: str = "fine_tuned_models/classification"):
        self.model_path = model_path
        self.fine_tuner = None
        self.is_loaded = False
        self.label_mappings = None
        
    def load_model(self) -> bool:
        """Load the fine-tuned model"""
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"Fine-tuned model not found at {self.model_path}")
                return False
            
            self.fine_tuner = ProductCategorizationFineTuner()
            success = self.fine_tuner.load_fine_tuned_model(self.model_path)
            
            if success:
                self.is_loaded = True
                self.label_mappings = self.fine_tuner.label_mappings
                logger.info("Fine-tuned model loaded successfully")
                return True
            else:
                logger.error("Failed to load fine-tuned model")
                return False
                
        except Exception as e:
            logger.error(f"Error loading fine-tuned model: {e}")
            return False
    
    def classify_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify product using fine-tuned model"""
        if not self.is_loaded:
            if not self.load_model():
                return self._fallback_classification(product_data)
        
        try:
            # Extract text for classification
            product_name = product_data.get('productDisplayName', '')
            description = product_data.get('description', '')
            
            # Combine name and description
            input_text = f"{product_name}. {description}".strip()
            
            if not input_text:
                return self._fallback_classification(product_data)
            
            # Make prediction
            prediction = self.fine_tuner.predict(input_text)
            
            # Map prediction to structured output
            result = self._map_prediction_to_structured_output(prediction, product_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in fine-tuned classification: {e}")
            return self._fallback_classification(product_data)
    
    def _map_prediction_to_structured_output(self, prediction: Dict[str, Any], product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map prediction to structured output format"""
        predicted_label = prediction['predicted_label']
        confidence = prediction['confidence']
        
        # Create structured output
        result = {
            'category': predicted_label,
            'subcategory': self._predict_subcategory(predicted_label, product_data),
            'confidence': confidence,
            'reasoning': f"Fine-tuned model prediction with {confidence:.2%} confidence"
        }
        
        return result
    
    def _predict_subcategory(self, category: str, product_data: Dict[str, Any]) -> str:
        """Predict subcategory based on category and product data"""
        # Simple rule-based subcategory prediction
        description = product_data.get('description', '').lower()
        product_name = product_data.get('productDisplayName', '').lower()
        text = f"{product_name} {description}"
        
        if category == 'Apparel':
            if any(word in text for word in ['shirt', 't-shirt', 'tshirt', 'top', 'blouse']):
                return 'Topwear'
            elif any(word in text for word in ['pants', 'jeans', 'trouser', 'shorts', 'skirt']):
                return 'Bottomwear'
            else:
                return 'Topwear'
        elif category == 'Footwear':
            return 'Shoes'
        elif category == 'Accessories':
            if any(word in text for word in ['watch', 'timepiece']):
                return 'Watches'
            elif any(word in text for word in ['bag', 'handbag', 'purse']):
                return 'Bags'
            else:
                return 'Watches'
        else:
            return 'General'
    
    def _fallback_classification(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback classification when fine-tuned model is not available"""
        logger.warning("Using fallback classification")
        
        description = product_data.get('description', '').lower()
        product_name = product_data.get('productDisplayName', '').lower()
        text = f"{product_name} {description}"
        
        # Simple rule-based classification
        if any(word in text for word in ['shoe', 'shoes', 'sneaker', 'boot', 'sandal']):
            category = 'Footwear'
            subcategory = 'Shoes'
        elif any(word in text for word in ['shirt', 't-shirt', 'tshirt', 'top', 'blouse', 'dress', 'pants', 'jeans']):
            category = 'Apparel'
            if any(word in text for word in ['shirt', 't-shirt', 'tshirt', 'top', 'blouse']):
                subcategory = 'Topwear'
            else:
                subcategory = 'Bottomwear'
        elif any(word in text for word in ['watch', 'bag', 'hat', 'cap', 'belt']):
            category = 'Accessories'
            subcategory = 'Watches' if 'watch' in text else 'Bags'
        else:
            category = 'Apparel'
            subcategory = 'Topwear'
        
        return {
            'category': category,
            'subcategory': subcategory,
            'confidence': 0.5,  # Lower confidence for fallback
            'reasoning': 'Fallback rule-based classification'
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.is_loaded:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_path": self.model_path,
            "label_mappings": self.label_mappings,
            "model_type": "fine_tuned"
        }
    
    def is_model_available(self) -> bool:
        """Check if fine-tuned model is available"""
        return os.path.exists(self.model_path) and self.is_loaded

# Global instance
fine_tuned_classifier = FineTunedCategoryClassifier()
